from book.handler import APIHandler
from sanic.response import json, text, html
import os
from book.model import User
from mongoengine.errors import NotUniqueError
from sanic.exceptions import InvalidUsage
import datetime
import copy
import json as pyjson
from book.web import error, generateSessionToken, log, AccountLock, validate
from bson import json_util
from bson import objectid


class index(APIHandler):

    async def get(self, requests):
        ''' query user'''
        # try:
        where = self.query_constraint(requests)
        # 返回的不是数组，就表示出现错误了
        if isinstance(where, tuple):
            return error(where[0], {'msg': where[1]})

        users = list()
        for user in User.get_users(where):
            users.append(user)

        data = {
            'body': {'results': users}
        }
        return json(**data)

    async def post(self, requests):
        '''
        user register
        '''
        request = requests.json

        if not isinstance(request, dict) or request is None:
            return error(107)

        if 'password' not in request:
            return error(201)
        if 'username' not in request:
            return error(200)
        if User.objects(username=request['username']).first() is not None:
            return error(202)

        # 生成 sessionToken
        sessionToken = generateSessionToken()
        request.update({
            'sessionToken': sessionToken,
            'createdAt': datetime.datetime.utcnow(),
            'updatedAt': datetime.datetime.utcnow(),
        })

        # 使用 from_json ，忽略掉多余的字段
        user = User.from_json(pyjson.dumps(request, default=json_util.default))
        user.save()

        data = {
            'body': {'sessionToken': user.sessionToken,
                     'objectId': str(user.id),
                     'createdAt': user.createdAt.isoformat(),
                     'updatedAt': user.updatedAt.isoformat(),
                     'username': user.username,
                     'emailVerified': user.emailVerified,
                     'mobilePhoneVerified': user.mobilePhoneVerified},
            'headers': {'Location': '/users/{}'.format(user.id)},
            'status': 201
        }
        return json(**data)


class user(APIHandler):

    @validate('uid')
    async def get(self, requests, uid):
        '''
        user login
        '''
        where = self.query_constraint(requests)
        # 返回的不是数组，就表示出现错误了
        if isinstance(where, tuple):
            return error(where[0], {'msg': where[1]})

        user = next(User.get_users(where, id=uid))
        if user is None: return error(211)

        data = {'body': user, 'status': 200}

        return json(**data)

    @validate('uid')
    async def put(self, requests, uid):
        '''
        update user information
        '''
        session = requests.json.get('X-LC-Session')
        user = User.objects(sessionToken=session).first()
        # user = User.objects(id=uid).first()
        if user is None:
            return error(211)
        if str(user.id) != uid:
            return error(206)

        data = requests.json
        data['updatedAt'] = datetime.datetime.utcnow()
        try:
            user.update(**data)
        except NotUniqueError as e:
            return error(202, result={'error': e})

        data = {
            'body': {'createdAt': user.updatedAt.isoformat()}
        }

        return json(**data)

    # @validate(uid='required')
    @validate('uid')
    async def delete(self, requests, uid):

        where = self.query_constraint(requests)
        if isinstance(where, tuple):
            return error(where[0], {'msg': where[1]})

        session = requests.headers.get('X-LC-Session')
        user = next(User.get_users(where, id=uid, raw=True)).first()

        if user is None:
            return error(211)
            
        user.delete()


class login(APIHandler):

    # @validate({'password':'required', 'username':'required'})
    async def post(self, requests):
        '''
        user login
        '''
        request = requests.json

        if not isinstance(request, dict) or request is None:
            return error(107)
        if 'password' not in request:
            return error(201)
        if 'username' not in request:
            return error(200)

        # 检测锁状态
        lock = AccountLock(username=request['username'])
        if lock.status is False:
            return error(lock.code, result={'data': {'ttl': lock.ttl, 'last_time': lock.last_time}})

        user = User.objects(**request).first()
        if user is None:
            # 用户名不存在
            if User.objects(username=request['username']).count() == 0:
                return error(211)
            # 帐号密码不匹配
            if User.objects(username=request['username'], password=request['password']).count() == 0:
                lock = AccountLock(username=request['username'])
                lock.lock()
                if lock.status is False:
                    return error(lock.code, result={'data': {'ttl': lock.ttl, 'last_time': lock.last_time}})
                return error(210, result={'data': {'last_time': lock.last_time}})

        log(requests, user=user, content='login')

        body = pyjson.loads(user.to_json())
        del body['_id']
        del body['password']
        body.update({
            'objectid': str(user.id),
            'createdAt': user.createdAt.isoformat(),
            'updatedAt': user.updatedAt.isoformat()
        })
        data = {'body': body, 'status': 200}
        return json(**data)


class refreshSessionToken(APIHandler):
    '''
    refresh sessionToken
    '''

    async def put(self, requests, objectid):
        # sessin = 'x-lc-session'
        # log(requests, username=user.username)

        session = requests.headers.get('X-LC-Session', '')
        user = User.objects(sessionToken=session).exclude('password').first()
        if user is None:
            return error(206)

        user.sessionToken = generateSessionToken()
        log(requests, user=user, content='refresh sessionToken')
        user.updatedAt = datetime.datetime.utcnow()
        log(requests, user=user, content='update updatedAt')
        user.save()

        body = pyjson.loads(user.to_json())
        del body['_id']
        body.update({
            'objectid': str(user.id),
            'createdAt': user.createdAt.isoformat(),
            'updatedAt': user.updatedAt.isoformat()
        })

        data = {'body': body, 'status': 200}
        return json(**data)


class updatePassword(APIHandler):
    '''
    security to modify password
    need old password and new password
    '''
    async def put(self, requests, uid):
        request = requests.json
        session = requests.headers.get('X-LC-Session')
        user = User.objects(sessionToken=session).first()

        if user is None:
            return error(206)
        if str(user.id) != uid:
            return error(206)

        if 'old_password' not in request:
            return error(201)
        if 'new_password' not in request:
            return error(201)

        if request['old_password'] != user.password:
            return error(210)

        user.password = request['new_password']
        user.updatedAt = datetime.datetime.utcnow()
        user.save()

        return json({'updatedAt': user.updatedAt.isoformat()})

        pass
