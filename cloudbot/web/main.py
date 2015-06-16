import cloudbot

from tornado import gen
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.platform.asyncio import AsyncIOMainLoop

from jinja2 import Environment, PackageLoader

from operator import attrgetter

wi = None


def get_template_env():
    env = Environment(loader=PackageLoader('cloudbot.web'))
    return env


def get_application():
    app = Application([
        (r'/', StatusHandler),
        (r'/factoids/?', TestHandler),
        (r'/commands/?', CommandsHandler),
        (r"/s/(.*)", StaticFileHandler, {"path": "./cloudbot/web/static"}),
    ], compress_response=True)
    return app


class TestHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        template = wi.env.get_template('basic.html')
        args = {
            'bot_name': wi.config.get('bot_name', 'CloudBot'),
            'bot_version': cloudbot.__version__,
            'heading': 'Placeholder Page',
            'text': 'Lorem ipsum!'
        }
        self.write(template.render(**args))


class StatusHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        template = wi.env.get_template('status.html')
        connections = {}
        for conn in wi.bot.connections:
            pass
        args = {
            'bot_name': wi.config.get('bot_name', 'Cloud  Butt'),
            'bot_version': cloudbot.__version__
        }
        self.write(template.render(**args))


class CommandsHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        template = wi.env.get_template('commands.html')
        commands = []

        for plugin in sorted(set(wi.bot.plugin_manager.commands.values()), key=attrgetter("name")):
            # use set to remove duplicate commands (from multiple aliases), and sorted to sort by name
            command = plugin.name

            aliases = ", ".join([i for i in plugin.aliases if not i == command])

            if aliases:
                cmd = "{} ({})".format(command, aliases)
            else:
                cmd = "{}".format(command)

            if plugin.doc:
                if plugin.doc.split()[0].isalpha():
                    doc = plugin.doc
                else:
                    doc = "{} {}".format(command, plugin.doc)
            else:
                doc = "Command has no documentation.".format(command)

            if plugin.permissions:
                perm = ", ".join(plugin.permissions)
            else:
                perm = None

            commands.append((cmd, doc, perm))

        args = {
            'bot_name': wi.config.get('bot_name', 'CloudBot'),
            'bot_version': cloudbot.__version__,
            'commands': commands
        }

        self.write(template.render(**args))


class WebInterface():
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config.get('web', {})

        self.port = self.config.get('port', 8090)
        self.address = self.config.get('address', '0.0.0.0')

        self.env = get_template_env()

        self.app = None

        global wi
        wi = self

        # Install tornado IO loop.
        AsyncIOMainLoop().install()

    def start(self):
        """ Starts the CloudBot web application """
        self.app = get_application()
        self.app.listen(self.port, address=self.address)
