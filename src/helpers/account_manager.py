import os
import json
from pathlib import Path
from ..helpers import Database
from .. import utils


class AccountManager:
    """Account manager class for superadmin operations."""

    def __init__(self, db: Database):
        self.db = db

    def change_superadmin_password(self, old_password: str, new_password: str) -> bool:
        """Change superadmin password with verification.

        Args:
            old_password: Current password for verification
            new_password: New password to set

        Returns:
            bool: True if password changed successfully

        Raises:
            ValueError: If validation fails
        """
        if not old_password.strip() or not new_password.strip():
            raise ValueError("Both old and new passwords are required")

        # Superadmin password is stored locally in a file
        password_file = Path.cwd() / 'superadmin_password.json'

        # Read current hashed password
        if os.path.exists(password_file):
            with open(password_file, 'r') as f:
                data = json.load(f)
                current_hashed = data.get('password')
        else:
            raise ValueError("Superadmin password not set")

        if not utils.verify_password(old_password, current_hashed):
            raise ValueError("Old password is incorrect")

        if utils.verify_password(new_password, current_hashed):
            raise ValueError("New password cannot be the same as the old password")

        # Hash new password and save
        hashed_pw = utils.hash_password(new_password)
        with open(password_file, 'w') as f:
            json.dump({'password': hashed_pw}, f)

        return True
