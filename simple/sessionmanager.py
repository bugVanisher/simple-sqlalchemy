#! /usr/bin/env python
# coding:utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session


class DBConfig():
    def __init__(self, host="", port=3306, user="", pwd="", db=""):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = db


class SessionFactory():
    '''
        session工厂类,支持多实例,多库,支持多线程
    '''
    sessions = {}
    is_debug = False

    @classmethod
    def set_debug(cls, lock=False):
        cls.is_debug = lock

    @classmethod
    def _get_name(cls, dbconfig):
        """

        :type dbconfig: DBConfig
        :rtype: str
        """
        if not dbconfig:
            return
        configs = [dbconfig.host, str(dbconfig.port), dbconfig.db, dbconfig.user]
        return "###".join(configs)

    @classmethod
    def get_session(cls, dbconfig):
        """
        :type dbconfig: DBConfig
        :rtype: Session
        """
        mapname = cls._get_name(dbconfig)
        if mapname not in cls.sessions.keys():
            cls.sessions[mapname] = []

        mysqlconnect = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}".format(
            user=dbconfig.user, password=dbconfig.pwd, host=dbconfig.host, port=dbconfig.port, database=dbconfig.db)
        engine = create_engine(mysqlconnect, echo=cls.is_debug, pool_size=10,
                               pool_recycle=18000)  # , poolclass=NullPool)
        # thread-local
        dbsession = scoped_session(
            sessionmaker(
                bind=engine,
                autoflush=True,
                autocommit=False,
            ))
        session = dbsession()
        cls.sessions[mapname].append(session)
        return session

    @classmethod
    def close_sessions(cls, dbconfig=None):
        '''
        :type dbconfig: DBConfig
        :return:
        '''
        mapname = cls._get_name(dbconfig)
        if mapname and mapname in cls.sessions.keys():  # close one session
            for session in cls.sessions[mapname]:
                session.close()
                print("close {name} session".format(name=mapname))
                return

        # close all sessions
        for k, s in dict.iteritems(cls.sessions):
            for session in s:
                session.close()
            print("close {name} session".format(name=k))
