#! /usr/bin/env python
# coding:utf-8

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.pool import NullPool


class DBConfig():
    def __init__(self, host="", port=3306, user="", pwd="", db=""):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = db


class SessionBase():
    '''
        session连接管理
    '''
    is_debug = True
    sessions = []

    @classmethod
    def set_debug(cls, lock=False):
        cls.is_debug = lock

    @classmethod
    def get_session(cls, dbconfig):
        """
        :type dbconfig: DBConfig
        :rtype: Session
        """
        # mysqlconnect = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}".format(
        #     user=dbconfig.user, password=dbconfig.pwd, host=dbconfig.host, port=dbconfig.port, database=dbconfig.db)
        # engine = create_engine(mysqlconnect, echo=cls.is_debug, pool_size=5, pool_recycle=7200)
        mysqlconnect = URL(drivername='mysql', username=dbconfig.user, password=dbconfig.pwd,
                           host=dbconfig.host, port=dbconfig.port, database=dbconfig.db)
        engine = create_engine(mysqlconnect, echo=cls.is_debug, poolclass=NullPool)
        # 禁用SQLAlchemy提供的数据库连接池，只需要在调用create_engine时指定连接池为NullPool，
        # SQLAlchemy就会在执行session.close()后立刻断开数据库连接
        # thread-local
        dbsession = scoped_session(
            sessionmaker(
                bind=engine,
                autoflush=True,
                autocommit=False,
            ))
        session = dbsession()
        cls.sessions.append(session)
        return session

    @classmethod
    def close_session(cls, session):
        '''
            close one session
        :type session:
        :return:
        '''
        if session in cls.sessions:
            session.close()
        print("close {} done.".format(session))

    @classmethod
    def close_sessions(cls):
        '''
            close all sessions
        :return:
        '''
        for session in cls.sessions:
            session.close()
        print("close sessions done.")
