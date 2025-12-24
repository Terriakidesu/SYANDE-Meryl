import mysql.connector

from typing import Optional

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

    @property
    def cursor(self):
        return self.db.cursor
