import os

from dotenv import load_dotenv

from models.secrets import Secrets


class Settings:

    def __init__(self) -> None:
        self.load_secrets()

        db_hostname = os.getenv("db_hostname")
        db_username = os.getenv("db_username")
        db_password = os.getenv("db_password")

        self._secrets = Secrets(db_hostname=db_hostname,
                                db_username=db_username,
                                db_password=db_password)

    def load_secrets(self) -> None:
        load_dotenv("secrets.env")

    @property
    def secrets(self):
        return self._secrets
