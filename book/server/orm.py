from server.database import Sqlite, Mysql
import collections
'''
ORM file
'''
class Field(object):
    def __init__(self, name, column_type, primary_key, auto_increment, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.auto_increment = auto_increment
        self.default = default

    def __str__(self):
        return '<{}:{}>'.format(self.__class__.__name__, self.name)

class StringField(Field):

    def __init__(self, name=None, primary_key=False, auto_increment=False,default='', ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, auto_increment,default)

class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, auto_increment=False,default=0, ddl='integer'):
        super().__init__(name, ddl, primary_key, auto_increment,default)

class ModelMetaclass(type):
    # 准备创建的类的对象，类名，父类集合，类方法集合
    def __new__(cls, name, bases, attrs):
        print("Found model:{}".format(name))
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)

        tableName = attrs.get('__table__', None) or name

        # 获取所有的 Fields 和主键名
        # mappings = dict()
        mappings = collections.OrderedDict()
        fields = []
        primaryKey = None
        print(type(attrs))
        for k, v in attrs.items():
            if isinstance(v, Field):
                print("Found mapping: {} ====> {}".format(k, v))
                mappings[k] = v
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError('Duplicate primary key for field: {}'.format(k))
                    primaryKey = k
                else:
                    fields.append(k)

                if v.auto_increment:
                    # 自增
                    auto_increment = k

        if not primaryKey:
            raise RuntimeError('Primary key not found.')

        for k in mappings.keys():
            attrs.pop(k)

        escaped_fields = list(map(lambda f:'`{}`'.format(f), fields))
        attrs['__mappings__'] = mappings
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey
        attrs['__auto_increment__'] = auto_increment
        attrs['__fields__'] = fields

        return type.__new__(cls, name, bases, attrs)


class DatabaseError(Exception):
    pass

class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, *args, **kw):
        super(Model, self).__init__(*args, **kw)
        self.attrs = kw
        self.__db = self.init_db()

    def init_db(self):
        '''
        初始化数据库
        返回数据库句柄
        '''
        conf = dict(engine='sqlite')
        return self.DatabaseFactory(self, engine='sqlite', sqlite=dict(db_file='server/data/server.db'))

    @classmethod
    def init_table(self):
        args = list()
        for k, v in self.__mappings__.items():
            var = k + ' '+v.column_type
            if k == self.__primary_key__:
                var += ' PRIMARY KEY'

            # if k == self.__auto_increment__:
            #     var += ' AUTO_INCREMENT'
            args += [var]

        args = ','.join(args)

        sql = 'CREATE TABLE if not exists {} ({})'.format(self.__table__, args)
        db = self.init_db(self)
        result = db.run(sql)
        return result


    def __getattr__(self, key):
        # print("__getattr__:{} > {}".format(key, self[key]))
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '{}'".format(key))

    def __setattr__(self, key, value):
        # print("__setattr__ : {}".format(key))
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)

        if value is None:
            # if key == self.__primary_key__:
            #
            fields = self.__mappings__[key]
            if fields.default is not None:
                value = fields.default() if callable(fields.default) else fields.default
                # print('using default value for {}:{}'.format(key, str(value)))
                setattr(self, key, value)

        return value

    def DatabaseFactory(self, *args, **kw):
        '''数据库工厂'''
        # print(kw)
        databases = {}
        databases['mysql'] = lambda *args, **kw: Mysql(*args, **kw)
        databases['sqlite'] = lambda *args, **kw: Sqlite(*args, **kw)

        engine = kw.get('engine')

        if engine in databases:
            configure = kw.get(engine)
            # print(kw.get('sqlite'))
            return databases[engine](*args, **configure)
        else:
            raise DatabaseError('指定的数据库：{} 暂不支持'.format(engine))

    def save(self):
        # print(self.getValueOrDefault(self.__fields__[0]))
        # return

        # args = list(map(self.getValueOrDefault, self.__fields__))
        # args.append(self.getValueOrDefault(self.__primary_key__))
        # print(args)
        args = dict()
        for k, _ in self.__mappings__.items():
            args[k] = self.getValueOrDefault(k)

        # print("Save method:")
        # print(args)
        # print(self.db)
        return

    def get_data(self):
        '''
        返回两个列表，
        fields 键
        args 值
        返回键值对
        '''
        args = list()
        fields = list()

        for k, _ in self.__mappings__.items():
            value = self.getValueOrDefault(k)
            if k == self.__primary_key__:
                '''主键为0时，设置为None'''
                if value == 0:
                    value = '{}'.format('NULL')
            elif isinstance(value, str):
                value = '\'{}\''.format(value)
            else:
                value = '{}'.format(value)

            fields.append('\'{}\''.format(k))
            args.append(value)

        return fields, args

    def insert(self):
        ''' insert data in table

        '''
        fields, args = self.get_data()
        tbl_name = self.__table__
        result = self.__db.insert(fields,tbl_name, args)

        print("INSERT RESULT")
        print(result)
        return result

    @classmethod
    def find(cls, where='', column='*'):
        '''query the table in the database

        Args:
            column: type of list, the column name to return, return all fields by default.
                example:
                    >>> find(column=['id', 'username'])
                    >>> find(column='id, username')
            where: Query parameters, the type of dictionary, the default is empty.
                example:
                    >>> find(where={'id':0})

        Returns:
            A list that contains instantiated class objects
            example:
                >>> [{'id':1, 'username':'luoxiaojie'}, {'id':2, 'username':'wufeifei'}]
                use:
                >>> user = User.find()
                >>> user[0].username
                >>> user[0].id
            if the data returned by the query is empty ,the empty listed is returned.
        '''
        db = cls.init_db(cls)


        if isinstance(column, str)  and column != '*':
            pass
        elif isinstance(column, list):
            column = ','.join(column)
        elif column == '*':
            column = ','.join([k for k,_ in cls.__mappings__.items()])

        find = db.find(column, cls.__table__, where)
        args = [list(k) for k in find]
        result = [cls(**dict(zip(column.split(','), k))) for k in args]

        return result

    @classmethod
    def find_one(cls, where='', column='*'):
        result = cls.find(where, column)
        # 弹出一个结果
        return result.pop()


    # @classmethod
    # def delete(cls):
    #     '''
    #     delete data from table
    #     '''
    #     fields = list()
    #     args = list()
    #     primary_value = cls.getValueOrDefault(cls,cls.__primary_key__)
    #     print(cls.__primary_key__)
    #     print(cls.getValueOrDefault(cls, cls.__primary_key__))
    #     if primary_value != 0:
    #         fields.append(cls.__primary_key__)
    #         args.append(primary_value)
    #     for k in cls.__fields__:
    #         fields.append(k)
    #         args.append(cls.getValueOrDefault(cls,k))
    #
    #     tbl_name = cls.__table__
    #     where = {k:'\'{}\''.format(v) for k, v in zip(fields, args)}
    #     print(where)
    #     db = cls.init_db(cls)
    #     result = db.delete(fields,tbl_name, where)
    #
    #     return result
    def delete(self):
        '''delete data from table
        '''
        fields = list()
        args = list()
        primary_value = self.getValueOrDefault(self.__primary_key__)
        # print(self.attrs)
        print(primary_value)
        if primary_value != 0:
            fields.append(self.__primary_key__)
            args.append(primary_value)
        # for k in self.__fields__:
        #     fields.append(k)
        #     args.append(self.getValueOrDefault(k))

        tbl_name = self.__table__
        where = {k:'\'{}\''.format(v) for k, v in zip(fields, args)}
        result = self.__db.delete(fields,tbl_name, where)

        return result

    def update(self, data):
        '''
        update data
        data: dict()
        '''
        print("This is Update method")
        print(self.attrs)
        print(type(data))
        if not isinstance(data, dict):
            raise Exception("data type must dict!")

        result = self.__db.update(self.__table__, data, self.attrs)
        return result

    @classmethod
    def count(cls, where='', column_name='*'):
        '''
        对应 sql count()函数
        返回数据表中指定列的值的数目
        当 where 为 '' 时，返回表中所有条数，
        否则按照 where 字典的限制条件返回查找到的条数
        '''
        db = cls.init_db(cls)
        result = db.count(cls.__table__, column_name, where)
        return result
