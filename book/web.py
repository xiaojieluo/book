from sanic.response import json
from book.codes import CODES
import hashlib
import os
from book.model import Log, App
import datetime
import redis


def error(code, result = None,*args, **kw):
    if code in CODES:
        data = {
            'body' : {'code' : code,
                        'error' : CODES[code]},
            'status' : 400
            }
        if result is not None:
            data['body'].update(result)
    else:
        data = {
            'body' :{'code':-1, 'error' : 'uncatch error:{}'.format(code)},
            'status' : 400
            }
    return json(**data)

def generateSessionToken():
    '''
    generate sessionToken
    '''
    return hashlib.sha1(os.urandom(24)).hexdigest()

class log(object):
    '''
    web log
    '''

    def __init__(self, requests, user='', content='', level=0):

        self.data = {
            'username' : user.username if user else '',
            'content' : content,
            'datetime' : datetime.datetime.utcnow(),
            'method' : requests.method,
            'version' : requests.version,
            'ip' : requests.ip[0],
            'port' : requests.ip[1],
            'user_agent' : requests.headers.get('user-agent', ''),
            'url' : requests.url,
            # 'schema' : requests.schema,
            'host' : requests.host,
            'query_string' : requests.query_string,
            'path' : requests.path,
            'level' : level,
            'app' : App.objects(appid=requests.headers.get('X-LC-Id', '')).first(),
            'user' : user
        }
        self.save()

    def save(self):
        '''
        save log
        '''
        log = Log(**self.data)
        log.save()

class AccountLock(object):
    '''
    帐号锁定
    Account lock
    '''
    # expire time: 900 seconds, 15 minute
    expire_sec = 900
    # max try length
    max_length = 6
    key = 'account:{}:login:fail'
    # last_time = 6

    def __init__(self, username, expire_sec=900, max_length=6):
        self.r = redis.Redis()

        self.expire_sec = expire_sec
        self.max_length = max_length
        self.key = self.key.format(username)
        self.status = True
        self.run()

    def run(self):
        '''
        检测锁状态
        check lock status(ttl and last_time)
        '''
        if self.ttl != 0 and self.last_time == 0:
            self.code = 219
            self.status = False
        else:
            self.status = True

    def lock(self):
        '''上锁'''
        self.r.incr(self.key)
        if self.r.exists(self.key) and self.r.ttl(self.key) is None:
            self.r.expire(self.key, self.expire_sec)

        if self.times >= 6:
            self.status = False

    @property
    def code(self):
        '''error code'''
        if hasattr(self, '_code'):
            return self._code

    @code.setter
    def code(self, value):
        value = int(value)
        self._code = value

    @property
    def times(self):
        '''已尝试次数'''
        if self.r.exists(self.key):
            tmp = self.r.get(self.key)
            num = int(tmp.decode())
        else:
            num = 0

        return num

    @property
    def last_time(self):
        num = self.max_length - self.times
        if num > 0:
            return num
        else:
            return 0

    @property
    def status(self):
        if self._status is False:
            self.code = 219

        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def ttl(self):
        print("ttl")
        if self.r.exists(self.key):
            # if self._ttl is None:
            # if not hasattr(self, '_ttl'):
            print(self.r.ttl(self.key))
            return self.r.ttl(self.key)

        return 0
            # return self._ttl

    # @ttl.setter
    # def ttl(self, value):
    #     self._ttl = value

if __name__ == '__main__':
    log()
