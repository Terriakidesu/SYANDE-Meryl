import mysql.connector

from typing import Optional, Any

from ..Settings import Settings


class Database:

    def __init__(self):
        self.connect()

    def connect(self):
        Settings.reload()

        self.db = mysql.connector.connect(
            host=Settings.secrets.db_hostname,
            user=Settings.secrets.db_username,
            password=Settings.secrets.db_password,
            database=Settings.secrets.db_database
        )

    def fetchAll(self, statement: str) -> list[Any]:
        return self.execute(statement).fetchall()

    def execute(self, statement: str):
        cursor = self.cursor()
        cursor.execute(statement)
        return cursor

    @property
    def cursor(self):
        return self.db.cursor
