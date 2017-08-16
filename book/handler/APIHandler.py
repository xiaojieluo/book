from sanic.views import HTTPMethodView
from sanic.response import json, text, raw, html
from book.model import User, App
import logging
import hashlib
from sanic.exceptions import InvalidUsage
from book.web import log

class APIHandler(HTTPMethodView):

    # def __init__(self):
    #     self.app = App(appid=)
    #     pass

    @classmethod
    async def authenticated(cls, requests):
        '''
        用户权限认证
        基于 appid 与 appkey

        appid
        appkey
        '''
        log(requests)
        logging.info('authenticated verification')
        id_name = 'X-LC-Id'
        key_name = 'X-LC-Key'
        sign_name = 'X-LC-Sign'

        headers = requests.headers

        app = App.objects(appid=headers.get(id_name, None)).first()
        if sign_name in headers:
            logging.info('use X-LC-Sign to verify application')
            sign = headers.get(sign_name)
            result = cls.SignVerify(cls, sign, app.appkey)
        else:
            logging.info('use X-LC-Id and X-LC-Key to verify application')
            appid = headers.get(id_name, None)
            appkey = headers.get(key_name, None)
            result = cls.KeyVerify(cls, app, appid, appkey)

        if result is False:
            return json({'msg':'Unauthorized'}, 401)


    def KeyVerify(self, app, appid, appkey):
        # 根据 appid 与 appkey 验证权限
        if isinstance(app, App):
            if app.appid == appid and app.appkey == appkey:
                return True

        return False

    def SignVerify(self, sign, appkey):
        # md5( timestamp + App Key )
        #     = md5( 1453014943466UtOCzqb67d3sN12Kts4URwy8 )
        #     = d5bcbb897e19b2f6633c716dfdfaf9be
        encrypt, timestamp = sign.split(',')
        md5 = hashlib.md5()
        md5.update(timestamp.encode('utf-8') + appkey.encode())

        if md5.hexdigest() == encrypt:
            return True

        return False

    @classmethod
    async def data_integrity_verification(cls, request):
        '''
        数据完整性验证
        '''
        log.info('Data integrity verification')
        # print('Data integrity verification')

    def verifyJson(self, requests):
        print(type(requests.json))
        print(not isinstance(requests.json, dict) or requests.json is None)
        # print(requests.json)
        # if requests.json is not None:
        # try:
        #     requests.json
        # except InvalidUsage as e:
        #     return json({'code':107, 'error':'Malformed json object. A json dictionary is expected.'})
        if not isinstance(requests.json, dict) or requests.json is None:
            return json({'code':107, 'error':'Malformed json object. A json dictionary is expected.'})

        return None
