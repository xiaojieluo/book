from book.handler import APIHandler
from sanic.response import json, text, html
import os
from book.model import User
from mongoengine.errors import NotUniqueError
from sanic.exceptions import InvalidUsage
import datetime
import copy
import json as pyjson
from book.web import error, generateSessionToken, log, AccountLock
from bson import json_util

class index(APIHandler):

    async def get(self, requests):
        '''
        user login
        '''
        return text("users")

    async def post(self, requests):
        '''
        user register
        '''
        request = requests.json

        if not isinstance(request, dict) or request is None:
            return error(107)

        if 'password' not in request: return error(201)
        if 'username' not in request: return error(200)
        if User.objects(username=request['username']).first() is not None:
            return error(202)

        # 生成 sessionToken
        sessionToken = generateSessionToken()
        request.update({
            'sessionToken' : sessionToken,
            'createdAt' : datetime.datetime.utcnow(),
            'updatedAt' : datetime.datetime.utcnow(),
        })

        # 使用 from_json ，忽略掉多余的字段
        user = User.from_json(pyjson.dumps(request, default=json_util.default))
        user.save()

        data = {
            'body' : {'sessionToken' : user.sessionToken,
                        'objectId' : str(user.id),
                        'createdAt' : user.createdAt.isoformat(),
                        'updatedAt' : user.updatedAt.isoformat(),
                        'username' : user.username,
                        'emailVerified' : user.emailVerified,
                        'mobilePhoneVerified' : user.mobilePhoneVerified},
            'headers' : {'Location' : '/users/{}'.format(user.id)},
            'status' : 201
        }
        return json(**data)

class login(APIHandler):

    async def post(self, requests):
        '''
        user login
        '''
        request = requests.json

        if not isinstance(request, dict) or request is None: return error(107)
        if 'password' not in request: return error(201)
        if 'username' not in request: return error(200)

        # 检测锁状态
        lock = AccountLock(username = request['username'])
        if lock.status is False:
            return error(lock.code, result={'data':{'ttl':lock.ttl,'last_time':lock.last_time}})

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
                    return error(lock.code, result={'data':{'ttl':lock.ttl, 'last_time':lock.last_time}})
                return error(210, result={'data':{'last_time':lock.last_time}})

        log(requests, user=user, content='login')

        body = pyjson.loads(user.to_json())
        del body['_id']
        del body['password']
        body.update({
            'objectid' : str(user.id),
            'createdAt' : user.createdAt.isoformat(),
            'updatedAt' : user.updatedAt.isoformat()
        })
        data = {'body' : body,'status' : 200}
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
        if user is None: return error(206)

        user.sessionToken = generateSessionToken()
        log(requests, user=user, content='refresh sessionToken')
        user.updatedAt = datetime.datetime.utcnow()
        log(requests, user=user, content='update updatedAt')
        user.save()

        body = pyjson.loads(user.to_json())
        del body['_id']
        body.update({
            'objectid' : str(user.id),
            'createdAt' : user.createdAt.isoformat(),
            'updatedAt' : user.updatedAt.isoformat()
        })

        data = {'body':body, 'status':200}
        return json(**data)
