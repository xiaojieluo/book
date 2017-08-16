from mongoengine import (connect, Document, StringField, DictField, ReferenceField, IntField, ListField,
                            BooleanField, ComplexDateTimeField, DateTimeField)
from mongoengine.errors import NotUniqueError
import time, datetime

connect('book')


class App(Document):
    username = StringField(required=True)
    appid = StringField(required=True)
    appkey = StringField(required=True)


class User(Document):

    # 用户名
    username = StringField(required=True)
    # 密码
    password = StringField(default='')
    # 昵称
    nickname = StringField(default='')
    # 手机号码, unique
    phone = StringField(default='')
    # 邮箱
    email = StringField(default='')
    age = IntField(default=18)
    tasks = ListField(ReferenceField('Task'))
    # 邮箱验证
    emailVerified = BooleanField(default=False)
    # 手机号码验证
    mobilePhoneVerified = BooleanField(default=False)
    # 登录验证用
    sessionToken = StringField(default='')
    createdAt = ComplexDateTimeField()
    updatedAt = ComplexDateTimeField()

    meta = {'strict': False}


class Task(Document):
    name = StringField(required=True)
    desc = StringField()
    tags = ListField(StringField())
    exp = IntField(default=0)
    money = IntField(default=0)
    expire = IntField(default=600)
    expire_type = IntField(default=1)
    status = IntField(default=1)
    announcer = ReferenceField('User')
    own = ReferenceField('User')
    comments = ListField(DictField())

class Log(Document):
    # 用户
    user = ReferenceField(User)
    # 用户名
    username = StringField()
    # app
    app = ReferenceField(App)
    # 操作内容
    content = StringField()
    # 操作时间
    datetime = DateTimeField()
    # HTTP 方法
    method = StringField()
    # HTTP 协议版本
    version = StringField()
    # 操作 ip
    ip = StringField()
    # 端口
    port = IntField()
    # 操作系统
    os = StringField()
    # 浏览器
    user_agent = StringField()
    # 链接
    url = StringField()
    # 请求链接格式
    schema = StringField()
    # 请求主机内容
    host = StringField()
    # 查询字符串
    query_string = StringField()
    # 请求路径
    path = StringField()
    # 日志等级， 0级正常操作， 1级调试， 2级警告， 3级
    level = IntField(default=0)




if __name__ == '__main__':
    # u = User(username='llnhhy')

    # a = App(username='xiaojieluoff',appid='FFnN2hso42Wego3pWq4X5qlu', appkey='UtOCzqb67d3sN12Kts4URwy8')
    # a.save()
    #
    # user = User(name="name")
    # # print(dir(a))
    # # print(a.id)
    # user.tasks.append(a.id)
    # user.save()
    # app = App.objectid(objectid=)
    # for user in User.objects:
    #     for task in user.tasks:
    #         # print(task)
    #         task = App.objects(id=task)
    #         print(help(task))
    #         print(task.appid)
    User.drop_collection()
    Task.drop_collection()
    Log.drop_collection()
    # user = User(fuck='fuck',username="llnhhy", password='1234',phone='123', createdAt=datetime.datetime.utcnow())
    # user.save(validate=False)
    #
    # print(User.objects(username='llnhhy')[0].createdAt.isoformat())
    # try:
    #     user.save()
    # except NotUniqueError as e:
    #     print(dir(e))
    #     print(e.with_traceback)
    # task = Task(name='give me a book')
    # task.save()
    # #
    # # user = User(name="xiaojieluo")
    # # user.tasks.append(task)
    # # user.save()
    #
    # for user in User.objects:
    #     for task in user.tasks:
    #         print(task.id)
