import unittest
from wallet_bot.credentials import Credentials
from wallet_bot.telegram.message import TelegramBotSession, \
    getMe, setWebhook, JsonWrapper
from wallet_bot.webserver.webserver import start_webserver
import requests
from time import sleep


class MessageTestCase(unittest.TestCase):

    def test_msg(self):
        webserver_cfg = Credentials.get_instance().db["webserver"]
        external_address = f"https://{webserver_cfg['webhook_hostname']}"

        session = TelegramBotSession()
        self.assertTrue(getMe(session).get()['is_bot'])

        webhook_request = {"url": external_address, "max_connections": 4}
        if "auth_secret" in webserver_cfg:
            webhook_request["secret_token"] = webserver_cfg["auth_secret"]

        setWebhook(session, webhook_request).get()

        with start_webserver() as q:
            print("Will receive messages and print them here")
            while True:
                chat_stuff = q.get()
                chat_stuff = JsonWrapper(chat_stuff)
                print(chat_stuff)

    def test_server(self):
        with start_webserver() as q:
            sleep(2)
            # test LAN connection
            webserver_cfg = Credentials.get_instance().db["webserver"]
            host_address = (f'{webserver_cfg["hostname"]}:'
                            f'{webserver_cfg["port"]}')
            print(f'GET http://{host_address}/hello')
            response = requests.get(f'http://{host_address}/hello')
            self.assertEqual(q.get(block=True), "queue response")
            self.assertEqual(response.text, "http response")
            # WAN connection
            external_address = f"https://{webserver_cfg['webhook_hostname']}"
            response = requests.get(external_address + '/hello')
            self.assertEqual(q.get(block=True), "queue response")
            self.assertEqual(response.text, "http response")
