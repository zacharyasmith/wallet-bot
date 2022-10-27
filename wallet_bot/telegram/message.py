import dataclasses
from wallet_bot.credentials import Credentials
import requests
from typing import Optional
from pprint import pformat
from collections.abc import Mapping


@dataclasses.dataclass(eq=False)
class TelegramBotCredentials:
    """Stores API credentials."""
    token: str
    name: int


@dataclasses.dataclass(repr=False, eq=False)
class JsonWrapper(Mapping):
    obj: dict

    def __repr__(self):
        return pformat(self.obj)

    def __getitem__(self, *args):
        return self.obj.__getitem__(*args)

    def __iter__(self):
        return self.obj.__iter__()

    def __len__(self):
        return self.obj.__len__()


class TelegramBotSession:
    """Defines the telegram bot session."""

    credentials: TelegramBotCredentials
    server_address: str

    def __init__(self,
                 credentials: Optional[TelegramBotCredentials] = None,
                 server_address: str = None):
        if credentials is not None:
            self.credentials = credentials
        else:
            creds = Credentials.get_instance().db
            self.credentials = TelegramBotCredentials(
                creds["telegram"]["token"], creds["telegram"]["bot_name"])
        if server_address:
            self.server_address = server_address
        else:
            self.server_address = creds["telegram"]["server_address"]
        self.base_address = \
            f"{self.server_address}/bot{self.credentials.token}"
        self.session = requests.session()

    def _form_path(self, path: str) -> str:
        return f"{self.base_address}/{path}"

    def post_json(self, path: str, obj: dict) -> requests.Response:
        """POST obj as json encoded."""
        print(f"POST {self.server_address}/bot***/{path}")
        return self.session.post(self._form_path(path), json=obj)


class TelegramError(BaseException):

    def __init__(self, description, error_code, context, **rest):
        super().__init__(
            f"When trying `{context}`, error code {error_code}: {description}")


class GetMessage:
    """GET Method."""

    session: TelegramBotSession
    path: str = "getUpdates"
    query: dict = dict()

    def __init__(self,
                 session: TelegramBotSession,
                 query: Optional[dict] = None,
                 path: str = None):
        """GET method: Specify path and query params as a dictionary."""
        self.session = session
        if path is not None:
            self.path = path
        if query:
            self.query = query

    def get(self):
        response = self.session.post_json(self.path, self.query)
        json_response = response.json()
        if 'ok' in json_response and not json_response['ok']:
            raise TelegramError(context=f"POST: {self.path}", **json_response)
        return JsonWrapper(json_response['result'])


class getChat(GetMessage):
    """https://core.telegram.org/bots/api#getchat"""
    path: str = "getChat"


class getMe(GetMessage):
    """https://core.telegram.org/bots/api#getme"""
    path: str = "getMe"


class setWebhook(GetMessage):
    """https://core.telegram.org/bots/api#setwebhook"""
    path: str = "setWebhook"


class logOut(GetMessage):
    """https://core.telegram.org/bots/api#logout"""
    path: str = "logOut"


class close(GetMessage):
    """https://core.telegram.org/bots/api#close"""
    path: str = "close"
