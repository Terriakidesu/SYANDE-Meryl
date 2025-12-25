from collections.abc import Sequence
from typing import Dict

import mysql.connector
from mysql.connector.abstracts import MySQLConvertibleType  # type: ignore

from ..Settings import Settings


class Database:

    def __init__(self):
        self.connect()

    def connect(self):
        Settings.reload()

        self._db = mysql.connector.connect(
            host=Settings.secrets.db_hostname,
            user=Settings.secrets.db_username,
            password=Settings.secrets.db_password,
            database=Settings.secrets.db_database
        )

    def fetchAll(self, statement: str, params: Sequence[MySQLConvertibleType] | Dict[str, MySQLConvertibleType] = ()):
        return self.execute(statement, params).fetchall()

    def fetchOne(self, statement: str, params: Sequence[MySQLConvertibleType] | Dict[str, MySQLConvertibleType] = ()):
        return self.execute(statement, params).fetchone()

    def commitOne(self, statement: str, params: Sequence[MySQLConvertibleType] | Dict[str, MySQLConvertibleType] = ()):
        cursor = self.execute(statement, params=params)
        self.db.commit()
        return cursor

    def commitMany(self, statement: str, params: Sequence[Sequence[MySQLConvertibleType] | Dict[str, MySQLConvertibleType]]):
        cursor = self.executeMany(statement, params)
        self.db.commit()
        return cursor

    def execute(self, statement: str, params: Sequence[MySQLConvertibleType] | Dict[str, MySQLConvertibleType] = ()):
        cursor = self.cursor(
            dictionary=True
        )
        cursor.execute(statement, params=params)
        return cursor

    def executeMany(self, statement: str, seq_params: Sequence[Sequence[MySQLConvertibleType] | Dict[str, MySQLConvertibleType]]):
        cursor = self.cursor()
        cursor.executemany(statement, seq_params=seq_params)
        return cursor

    @property
    def cursor(self):
        return self.db.cursor

    @property
    def db(self):
        return self._db
