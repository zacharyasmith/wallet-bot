"""Telegram webhook server."""

from wallet_bot.credentials import Credentials
from flask import Flask, request, abort
import os
import contextlib
import multiprocessing
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app(q: multiprocessing.Queue, **kwargs):

    app = Flask(__name__)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    webserver_cfg = Credentials.get_instance().db["webserver"]

    @app.route('/', methods=['POST', 'GET'])
    def index():
        if "auth_secret" in webserver_cfg:
            authenticated = request.method == 'GET'
            for name, value in request.headers:
                if name == "X-Telegram-Bot-Api-Secret-Token" and \
                   value == webserver_cfg["auth_secret"]:
                    authenticated = True
            if not authenticated:
                abort(500)
        if request.method == 'POST':
            q.put(request.get_json())
        return ''

    @app.route('/hello')
    def hello_world():
        q.put("queue response")
        return "http response"

    if webserver_cfg["behind_proxy"]:
        app.wsgi_app = ProxyFix(app.wsgi_app,
                                x_for=1,
                                x_proto=1,
                                x_host=1,
                                x_prefix=1)

    app.run(**kwargs)


@contextlib.contextmanager
def start_webserver(*args, **kwargs):
    webserver = Credentials.get_instance().db["webserver"]
    configuration = {
        "threaded": True,
        "use_reloader": False,
        "use_debugger": True,
        "debug": True,
        "host": webserver["hostname"],
        "port": webserver["port"]
    }
    configuration.update(kwargs)
    q = multiprocessing.Queue()

    try:
        p = multiprocessing.Process(target=create_app,
                                    name=__name__,
                                    args=(q, ),
                                    kwargs=configuration)
        p.start()
        yield q
    finally:
        p.terminate()
