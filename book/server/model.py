from server.database import DatabaseFactory
from dove.settings import Setting
from dove.app import Article
from server.database import Sqlite, Mysql
from server.orm import Model, IntegerField, StringField
import time, uuid
import json


class Article(Model):

    id = IntegerField(primary_key=True, auto_increment=True)
    data = StringField()

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            # 将返回的 json 格式数据转换成 dict 格式
            data = json.loads(self.get('data', {}))
            return data.get(key, None)
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '{}'".format(key))


class Page(Model):
    id = IntegerField(primary_key=True, auto_increment=True)
    data = StringField()

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            # 将返回的 json 格式数据转换成 dict 格式
            data = json.loads(self.get('data', {}))
            return data.get(key, None)
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '{}'".format(key))        
