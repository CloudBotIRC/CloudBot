import asyncio

from tornado import gen
from tornado.web import RequestHandler, Application, url
from tornado.platform.asyncio import AsyncIOMainLoop

from jinja2 import Environment, PackageLoader


def get_template_env():
    env = Environment(loader=PackageLoader('cloudbot.web.templates'))
    return env


def get_application():
    app = Application([
        url('/', TestHandler)
    ])
    return app


class TestHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        self.write("Hello world!\n")


class WebInterface():
    def __init__(self, bot, port=8080, address="0.0.0.0"):
        self.bot = bot
        self.port = port
        self.address = address

        self.template = get_application()
        self.template_env = get_template_env()

        self.app = None

        # Install tornado IO loop.
        AsyncIOMainLoop().install()

    def start(self):
        """ Starts the CloudBot web application """
        self.app = get_application()
        self.app.listen(self.port, address=self.address)
