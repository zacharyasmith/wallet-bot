"""Unit tests for credentials.py."""

from unittest import TestCase
from tempfile import TemporaryDirectory
from pathlib import Path
from wallet_bot.credentials import Credentials
from typing import Optional


class TestCredentials(TestCase):

    def credentials_helper(self,
                           credentials,
                           assert_raises: Optional[type] = None) -> dict:
        with TemporaryDirectory() as d:
            d = Path(d)
            credentials_file = d / 'creds.json'
            with credentials_file.open('w') as f:
                f.write(credentials)
            cred = Credentials(credentials_file)
            return cred.db

    def test_credentials_good(self):
        db = self.credentials_helper("""\
        {
        "telegram": {
        "token": "123:ABCD",
        "bot_name": "BotBae",
        "server_address": "https://api.telegram.org",
        "chat": -100
        },
        "webserver": {
        "hostname": "my-mbp",
        "port": 5000,
        "behind_proxy": true,
        "auth_secret": "mysecret",
        "webhook_hostname": "behindmyproxy.org"
        }
        }
        """)
        self.assertEqual(db["telegram"]["token"], '123:ABCD')
