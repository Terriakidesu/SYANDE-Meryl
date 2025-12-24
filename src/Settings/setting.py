import os

from dotenv import load_dotenv

from .models import Secrets

SECRETS_PATH = os.path.join(os.getcwd(), "secrets.env")


class SettingsClass:

    def __init__(self) -> None:
        self.load_secrets()

    def load_secrets(self) -> None:
        load_dotenv(SECRETS_PATH)

        db_hostname = os.getenv("db_hostname")
        db_username = os.getenv("db_username")
        db_password = os.getenv("db_password")
        db_database = os.getenv("db_database")

        self._secrets = Secrets(db_hostname=db_hostname,
                                db_username=db_username,
                                db_password=db_password,
                                db_database=db_database)

    def reload(self):
        self.load_secrets()

    @property
    def secrets(self):
        return self._secrets
