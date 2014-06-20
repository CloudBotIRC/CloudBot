import asyncio

from watchdog.observers import Observer
from watchdog.tricks import Trick


class PluginReloader(object):
    def __init__(self, bot):
        """
        :type bot: cloudbot.bot.CloudBot
        """
        self.observer = Observer()
        self.bot = bot
        self.reloading = set()
        self.event_handler = PluginEventHandler(self, patterns=["*.py"])

    def start(self, module_path):
        """Starts the plugin reloader
        :type module_path: str
        """
        self.observer.schedule(self.event_handler, module_path, recursive=False)
        self.observer.start()

    def stop(self):
        """Stops the plugin reloader"""
        self.observer.stop()

    def reload(self, path):
        """
        Loads or reloads a module, given its file path. Thread safe.

        :type path: str
        """
        if isinstance(path, bytes):
            path = path.decode()
        self.bot.loop.call_soon_threadsafe(lambda: asyncio.async(self._reload(path), loop=self.bot.loop))

    @asyncio.coroutine
    def _reload(self, path):
        if path in self.reloading:
            # we already have a coroutine reloading
            return
        self.reloading.add(path)
        # we don't want to reload more than once every 200 milliseconds, so wait that long to make sure there
        # are no other file changes in that time.
        yield from asyncio.sleep(0.2)
        self.reloading.remove(path)
        yield from self.bot.plugin_manager.load_plugin(path)


class PluginEventHandler(Trick):
    def __init__(self, loader, *args, **kwargs):
        """
        :type loader: PluginReloader
        """
        super().__init__(*args, **kwargs)
        self.loader = loader

    def on_created(self, event):
        self.loader.reload(event.src_path)

    def on_modified(self, event):
        self.loader.reload(event.src_path)

    def on_moved(self, event):
        # only load if it's moved to a .py file
        if event.dest_path.endswith(".py" if isinstance(event.dest_path, str) else b".py"):
            self.loader.reload(event.dest_path)
