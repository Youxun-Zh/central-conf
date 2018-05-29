"""
"""
__author__ = "xiaoweizhong"
__email__ = "xiaoweizhong@sohu-inc.com"
__date__ = "11-03-2016 14:00"

import MySQLdb
import sqlalchemy
from settings import DATABASES, ENGINE_URL, MYSQLPOOL_ARGUMENTS


class MysqlClient():
    """The class for execute mysql operation.
    """
    def __init__(self, using=True):
        db_key = "default"
        if not using:
            db_key = "default-slave"
        self.db_config = DATABASES.get(db_key, {})

        # self.db = self.get_db(db_config)
        self.db = self.get_db_by_engine(self.db_config)
        self.db.execute = self.execute
        self.db.executemany = self.executemany

    def get_db(self, db_config):
        # TODO: pool
        db_config = {key.lower(): val for key, val in db_config.items()}
        conn = MySQLdb.connect(**db_config)
        return conn

    def get_db_by_engine(self, db_config):
        # TODO: pool
        engine_url = ENGINE_URL.format(p=db_config)
        engine = sqlalchemy.create_engine(engine_url, poolclass=sqlalchemy.pool.QueuePool, **MYSQLPOOL_ARGUMENTS)
        conn = engine.raw_connection()
        return conn

    def execute_func(self, sql, params, attr, flag):
        self.db = self.get_db_by_engine(self.db_config)
        cursor = self.db.cursor()
        func = getattr(cursor, attr)
        data, num = (), 0
        try:
            num = func(sql, params)
            data = cursor.fetchall() if flag else cursor.fetchone()
        except Exception as e:
            self.db.rollback()
        else:
            self.db.commit()
        finally:
            cursor.close()
            self.db.close()
        return data, num

    def execute(self, sql, params, flag=False):
        data = self.execute_func(sql, params, "execute", flag)
        return data

    def executemany(self, sql, params, flag=True):
        data = self.execute_func(sql, params, "execute", flag)
        return data