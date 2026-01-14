from collections.abc import Sequence
from typing import Dict, Any

import mysql.connector
from mysql.connector.abstracts import MySQLConvertibleType  # type: ignore

from ..Settings import Settings


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.connect()

    def connect(self):
        Settings.reload()

        max_retries = 3
        for attempt in range(max_retries):
            try:
                self._db = mysql.connector.connect(
                    host=Settings.secrets.db_hostname,
                    user=Settings.secrets.db_username,
                    password=Settings.secrets.db_password,
                    database=Settings.secrets.db_database
                )
                break  # Connection successful
            except mysql.connector.Error as e:
                if attempt == max_retries - 1:
                    raise  # Re-raise the exception after the last attempt
                # Continue to the next retry attempt

    def fetchAll(self, statement: str, params: Sequence[MySQLConvertibleType] | Dict[str, MySQLConvertibleType] = ()) -> list[Dict[str, Any]]:
        return self.execute(statement, params).fetchall()  # type: ignore

    def fetchOne(self, statement: str, params: Sequence[MySQLConvertibleType] | Dict[str, MySQLConvertibleType] = ()) -> Dict[str, Any] | None:
        return self.execute(statement, params).fetchone()  # type: ignore

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
