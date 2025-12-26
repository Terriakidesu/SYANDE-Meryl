import os
import json
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import ValidationError

from .models import Secrets, Properties

logger = logging.getLogger(__name__)


class SettingsClass:
    _instance: Optional['SettingsClass'] = None

    def __new__(cls) -> 'SettingsClass':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        self._properties: Optional[Properties] = None
        self._secrets: Optional[Secrets] = None

        self.load_properties()
        self.load_secrets()

    def load_properties(self) -> None:
        """Load properties from properties.json with error handling."""
        properties_path = Path("properties.json")
        if not properties_path.exists():
            raise FileNotFoundError(f"Properties file not found: {properties_path}")

        try:
            with open(properties_path, "r", encoding="utf-8") as f:
                properties_json = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in properties file: {e}")
            raise

        try:
            properties = Properties(**properties_json)
        except ValidationError as e:
            logger.error(f"Invalid properties configuration: {e}")
            raise

        self._properties = properties
        self.env = properties.env
        self.profiles = properties.profiles
        logger.info("Properties loaded successfully")

    def load_secrets(self) -> None:
        """Load secrets from environment variables with validation."""
        env_path = getattr(self.env, 'path', None)
        if env_path and Path(env_path).exists():
            load_dotenv(env_path)
            logger.info(f"Loaded environment from {env_path}")
        else:
            load_dotenv()  # Load from default locations
            logger.info("Loaded environment from default locations")

        # Get environment variables with defaults/fallbacks
        db_hostname = os.getenv("DB_HOSTNAME", "localhost")
        db_username = os.getenv("DB_USERNAME", "")
        db_password = os.getenv("DB_PASSWORD", "")
        db_database = os.getenv("DB_DATABASE", "")

        # Validate required secrets
        if not db_username or not db_password or not db_database:
            logger.warning("Some database credentials are missing from environment variables")

        try:
            self._secrets = Secrets(
                db_hostname=db_hostname,
                db_username=db_username,
                db_password=db_password,
                db_database=db_database
            )
        except ValidationError as e:
            logger.error(f"Invalid secrets configuration: {e}")
            raise

        logger.info("Secrets loaded successfully")

    def reload(self) -> None:
        """Reload secrets from environment."""
        logger.info("Reloading secrets")
        self.load_secrets()

    @property
    def secrets(self) -> Secrets:
        """Get secrets with lazy loading."""
        if self._secrets is None:
            self.load_secrets()
        assert self._secrets is not None
        return self._secrets

    @property
    def properties(self) -> Properties:
        """Get properties."""
        if self._properties is None:
            self.load_properties()
        assert self._properties is not None
        return self._properties

    def get_database_url(self) -> str:
        """Generate database connection URL."""
        s = self.secrets
        return f"mysql://{s.db_username}:{s.db_password}@{s.db_hostname}/{s.db_database}"

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return getattr(self.env, 'name', '').lower() == 'development'

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return getattr(self.env, 'name', '').lower() == 'production'


# Global instance
Settings = SettingsClass()
