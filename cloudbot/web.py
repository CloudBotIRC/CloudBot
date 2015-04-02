import asyncio

from tornado.web import RequestHandler, Application, url
from tornado.platform.asyncio import AsyncIOMainLoop


def get_application():
    app = Application([
        url('/', TestHandler)
    ])
    return app


class TestHandler(RequestHandler):
    def get(self):
        self.write("Hello world!\n")


class WebInterface():
    def __init__(self, bot, port=8080, address="0.0.0.0"):
        self.bot = bot
        self.port = port
        self.address = address

        self.app = None

        # Install tornado IO loop.
        AsyncIOMainLoop().install()

    def start(self):
        """ Starts the CloudBot web application """
        self.app = get_application()
        self.app.listen(self.port, address=self.address)
