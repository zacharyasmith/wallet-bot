"""Credentials and secrets."""

from wallet_bot.common import ROOT
import jsonschema
import json
from typing import Any
from os import PathLike
from pathlib import Path

CREDENTIALS_FILE = ROOT / 'credentials.json'
SCHEMA_FILE = ROOT / 'credentials.schema.json'


class Credentials:
    """Credentials class for secrets."""

    __instance = None
    db: dict = None

    @classmethod
    def get_instance(cls):
        """Get instance of singleton."""
        if Credentials.__instance is None:
            Credentials.__instance = Credentials()
        return Credentials.__instance

    def __init__(self, credentials_file: PathLike = CREDENTIALS_FILE):
        """Create Credentials."""
        self.reload(Path(credentials_file))

    def reload(self, credentials_file: Path):
        """Reload the values from the creds file."""
        with SCHEMA_FILE.open() as f:
            schema = json.loads(f.read())
        with credentials_file.open() as f:
            creds = json.loads(f.read())
        # validate the file conforms to the schema
        try:
            jsonschema.validate(creds, schema)
        except Exception as e:
            raise ValueError(
                f"Failed to validate {credentials_file.name}") from e
        # set the db
        self.db = creds

    @classmethod
    def get(cls, name: str, default: Any = None):
        return cls.get_instance().db.get(name, default)
