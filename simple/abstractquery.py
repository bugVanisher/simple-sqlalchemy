#! /usr/bin/env python
# coding:utf-8
import sys

from sqlalchemy import func, distinct, inspect
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.query import Query

from sessionmanager import *

__author__ = 'heyu'
"""
    added at 2015-08-01
"""


class OperateType:
    EQUALS = "="
    NOT_EQUALS = "!="
    LARGER = ">"
    LARGER_AND_EQUALS = ">="
    LESS = "<"
    LESS_AND_EQUALS = "<="
    IN = "in"
    NOT_IN = "not in"
    IS_NULL = "is null"
    IS_NOT_NULL = "is not null"
    LIKE = "like"


class JoinType:
    AND_JOIN = "and"
    OR_JOIN = "or"


class Bind:
    """
        单个列具体的查询条件
    """

    def __init__(self, fieldname="", operate_type=OperateType.EQUALS, join_type=JoinType.AND_JOIN, value=None):
        self.fieldname = fieldname
        # "=", "!=", "<", ">", "<=", ">=", "<>", "in", "like", "><" ,"is null","is not null"
        self.operate_type = operate_type
        # and or
        self.join_type = join_type
        # condition value
        self.value = value

    def __repr__(self):
        return "<{classname}:fieldname({field}),operatorType({operator}),joinType({join}),value({value})>".format(
            classname=self.__class__.__name__, field=self.fieldname, operator=self.operate_type, join=self.join_type,
            value=self.value)


class BaseQuery():
    """
        query对象的父类 查询类继承
    """
    _page = None  # 第几页开始
    _count = None  # 取多少个
    _order_by = []  # 排序字段,支持多个

    def set_page(self, page):
        if page < 0:
            sys.exit("page illegal")
        self._page = page

    def get_page(self):
        return self._page

    def set_count(self, count):
        if count < 1:
            sys.exit("count illegal")
        self._count = count

    def get_count(self):
        return self._count

    def set_order(self, sort):
        if not isinstance(sort, Sort):
            sys.exit("sort obj illegal")
        self._order_by.append(sort)

    def get_order(self):
        return self._order_by


class Sort():
    """
        排序字段
    """

    def __init__(self, order_by, sort_type=True):
        self.order_by = order_by
        self.sort_type = sort_type  # 排序类型,默认是升序


class BindAttrField:
    """
        query字段装饰器
    """

    def __init__(self, field, operate_type, join_type):
        self.field = field
        self.operate_type = operate_type
        self.join_type = join_type

    def __call__(self, fn):
        def wrapped(*args):
            self_obj, value = self._get_value(args)
            bind = Bind(self.field, self.operate_type, self.join_type, value)
            atuple = (self_obj, bind)
            return fn(*atuple)

        return wrapped

    def _get_value(self, args):
        if len(args) != 2:
            sys.exit("BindAttrField's params error: {}".format(args))
        return args[0], args[1]


class CloseSession:
    """
        关闭数据库连接,对于守护进程,还是使用下好
    """

    def __init__(self, dbconfig=None):  # 装饰器@CloseSession在方法结束后关闭数据库连接
        """
        :type dbconfig: DBConfig
        """
        self.dbconfig = dbconfig

    def __call__(self, fn):
        def wrapped(*args, **kwargs):
            result = fn(*args, **kwargs)
            if self.dbconfig:
                SessionFactory.close_sessions(self.dbconfig)
            else:
                SessionFactory.close_sessions()
            return result

        return wrapped


class Dal():
    """
        封装数据库操作的抽象类,支持多线程
    """

    def __init__(self, dbconfig=None):
        # 直接实例化,若使用多线程则重复实例化即可
        """

        :type dbconfig: DBConfig
        """
        if not isinstance(dbconfig, DBConfig):
            raise Exception("not a DBConfig obj")
        self.session = SessionFactory.get_session(dbconfig)
        self.dbconfig = dbconfig

    def _generate_conditon(self, column, attr_field):
        """
            根据操作符返回sqlachemy的参数化条件对象
        :type column: InstrumentedAttribute
        :type attr_field: Bind
        :return:
        """
        statement = object
        if OperateType.EQUALS == attr_field.operate_type:
            statement = column == attr_field.value
        elif OperateType.NOT_EQUALS == attr_field.operate_type:
            statement = column != attr_field.value
        elif OperateType.LARGER == attr_field.operate_type:
            statement = column > attr_field.value
        elif OperateType.LARGER_AND_EQUALS == attr_field.operate_type:
            statement = column >= attr_field.value
        elif OperateType.LESS == attr_field.operate_type:
            statement = column < attr_field.value
        elif OperateType.LESS_AND_EQUALS == attr_field.operate_type:
            statement = column <= attr_field.value
        elif OperateType.LIKE == attr_field.operate_type:
            statement = column.like(attr_field.value)  # %要自己传入
        elif OperateType.IS_NULL == attr_field.operate_type:
            statement = column == None
        elif OperateType.IS_NOT_NULL == attr_field.operate_type:
            statement = column != None
        elif OperateType.IN == attr_field.operate_type:
            if isinstance(attr_field.value, str):
                print("{param} should be a list or a tuple not str".format(param=attr_field.value))
            statement = column.in_(attr_field.value)
        elif OperateType.NOT_IN == attr_field.operate_type:
            if isinstance(attr_field.value, str):
                print("{param} should be a list or a tuple not str".format(param=attr_field.value))
            statement = ~column.in_(attr_field.value)
        else:
            print("{operator} is not supported".format(operator=attr_field.operate_type))
        return statement

    def _select_fields(self, select_field):
        if isinstance(select_field, type):
            baseQuery = self.session.query(select_field)
        else:
            if isinstance(select_field, InstrumentedAttribute):
                baseQuery = self.session.query(select_field)
            else:
                baseQuery = self.session.query(*select_field)
        return baseQuery

    def _combine(self, base_query, condition):
        """
            组装where条件
        :type base_query: Query
        :type condition: BaseQuery
        :rtype: Query
        """
        # try:
        if not isinstance(condition, BaseQuery):
            raise Exception("请传入BaseQuery的实例")

        cond = []
        for attr in dir(condition):
            obj_attr = getattr(condition, attr)
            if isinstance(obj_attr, Bind):
                cond.append(obj_attr)

        ands = []
        ors = []
        for item in cond:
            attr_field = item
            ":type: Bind"

            if OperateType.IS_NULL != attr_field.operate_type and OperateType.IS_NOT_NULL != attr_field.operate_type:
                if attr_field.value is None or type(attr_field.value) == bool:
                    continue
            if JoinType.OR_JOIN == attr_field.join_type:
                ors.append({attr_field.fieldname: attr_field})
            elif JoinType.AND_JOIN == attr_field.join_type:
                ands.append({attr_field.fieldname: attr_field})
        # and condition
        real_and_conditions = []
        for a in ands:
            for k, v in dict.items(a):
                real_and_conditions.append(self._generate_conditon(k, v))

        # or condition
        real_or_conditions = []
        for o in ors:
            for k, v in dict.items(o):
                real_or_conditions.append(self._generate_conditon(k, v))
        # logical
        exp_and, exp_or = True, False
        for i in range(len(real_and_conditions)):
            exp_and = real_and_conditions[i] & exp_and

        for i in range(len(real_or_conditions)):
            exp_or = real_or_conditions[i] | exp_or

        if len(real_and_conditions) == 0 and len(real_or_conditions) == 0:
            pass
        if len(real_and_conditions) == 0 and len(real_or_conditions) > 0:
            base_query = base_query.filter(exp_or)
        else:
            base_query = base_query.filter(exp_and | exp_or)
        base_query = self._order_handler(base_query, condition.get_order())
        base_query = self._limit_handler(base_query, condition.get_page(), condition.get_count())
        return base_query

        # except Exception as e:
        #     print("组装where子句错误{error}".format(error=e))

    def _limit_handler(self, base_query, page, count):
        """
            limit condition
        :param page:
        :param count:
        :return:
        """
        if not page and count:
            return base_query.slice(0, count)
        elif page and not count:
            sys.exit("please set count")
        elif not page and not count:
            return base_query
        offset = (page - 1) * count
        if offset <= 0:
            base_query = base_query.slice(0, count)
        else:
            base_query = base_query.slice(offset, offset + count)
        return base_query

    def _order_handler(self, base_query, order_fields):
        """
            order by
        :param order_fields:
        :return:
        """
        if not order_fields:
            return base_query
        for sort in order_fields:
            order_field = sort
            """:type order_field:Sort"""
            if order_field.sort_type:
                base_query = base_query.order_by(order_field.order_by)
            else:
                base_query = base_query.order_by(order_field.order_by.desc())
        return base_query

    def get_distinct_field(self, field, condition):
        """
            返回去重的列,是非orm的list类型
        :param field:
        :param condition:
        :return:
        """
        baseQuery = self.session.query(field).distinct()
        baseQuery = self._combine(baseQuery, condition)
        return baseQuery.all()

    @DeprecationWarning
    def conbine_query_in_groups(self, select_field, group_conditions):
        """
            use self_group()  & |
        :param condition:
        :return:

        demo
            ((Lobby.id == Team.lobby_id) &
                (LobbyPlayer.team_id == Team.id) &
                        (LobbyPlayer.player_id == player.steamid)).self_group() |
                        ((Lobby.id == spectator_table.c.lobby_id) &
                                (spectator_table.c.player_id == player.steamid)).self_group()

        """
        baseQuery = self._select_fields(select_field)
        return baseQuery.filter(group_conditions).all()

    def save(self, obj):
        """
            insert one record
        :param obj:
        :return:
        """
        try:
            self.session.add(obj)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def get_list(self, select_field, condition):
        """
            返回orm对象list 如果selectField不是orm对象则返回简单的list
        :param select_field:
        :param condition:
        :return:
        """
        base_query = self._select_fields(select_field)
        base_query = self._combine(base_query, condition)

        try:
            return base_query.all()
        except Exception, e:
            raise Exception(e)

    def get(self, pks, ddl_class):
        """

        :param pks:
        :param ddl_class:
        :return: ddl_class
        """
        if not isinstance(pks, (list, tuple)):
            pks = [pks]
        primary_key = inspect(ddl_class).primary_key[0]
        base_query = self.session.query(ddl_class).filter(primary_key.in_(pks))
        try:
            return base_query.all()
        except Exception, e:
            raise Exception(e)

    def batch_save(self, objs):
        """

        :type objs: list
        :rtype: bool
        """
        try:
            if not isinstance(objs, (list, tuple)):
                return False
            self.session.add_all(objs)
            self.session.commit()
            return True
        except Exception, e:
            print(e)
            self.session.rollback()
            return False

    def save_or_update(self, obj):
        """
            插入或更新 base on primary key
        :param obj:
        :return:
        """
        try:
            count = self.session.merge(obj)
            self.session.commit()
            return count
        except Exception:
            self.session.rollback()
            return False

    def update(self, obj, update_dict, condition):
        """
            update on condition
        :param obj:
        :param update_dict:
        :param condition:
        :return:
        """
        try:
            base_query = self.session.query(obj)
            base_query = self._combine(base_query, condition)
            count = base_query.update(update_dict, synchronize_session=False)
            self.session.commit()
            return count
        except Exception, e:
            self.session.rollback()
            return False

    def delete(self, obj, condition):
        """
            delete on condition
        :param obj:
        :param condition:
        :return:
        """
        try:
            base_query = self.session.query(obj)
            base_query = self._combine(base_query, condition)
            count = base_query.delete(synchronize_session=False)
            self.session.commit()
            return count
        except Exception:
            self.session.rollback()
            return False

    def count(self, single_select_field, condition):
        """
            计算数量
        :type single_select_field: InstrumentedAttribute
        :type condition:
        :rtype:
        """
        base_query = self.session.query(func.count(single_select_field))
        base_query = self._combine(base_query, condition)
        result = base_query.one()
        return result

    def distinct_count(self, select_field, condition):
        """
            排重计算
        :param select_field:
        :param condition:
        :return:
        """
        base_query = self.session.query(func.count(distinct(select_field)))
        base_query = self._combine(base_query, condition)
        return base_query.one()

    def execute(self, raw_sql):
        """

        :type raw_sql: str
        :rtype: sqlalchemy.engine.result.ResultProxy
        """
        try:
            result = self.session.execute(raw_sql)
            self.session.commit()
            return result
        except Exception:
            self.session.rollback()
            return None

    def close(self):
        SessionFactory.close_sessions(self.dbconfig)
