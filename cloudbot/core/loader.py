import asyncio
import os

from watchdog.observers import Observer
from watchdog.tricks import Trick


class PluginLoader(object):
    def __init__(self, bot):
        """
        :type bot: cloudbot.core.bot.CloudBot
        """
        self.observer = Observer()
        self.module_path = os.path.abspath("plugins")
        self.bot = bot

        self.event_handler = PluginEventHandler(self, patterns=["*.py"])
        self.observer.schedule(self.event_handler, self.module_path, recursive=False)

    def start(self):
        """Starts the plugin reloader"""
        self.observer.start()

    def stop(self):
        """Stops the plugin reloader"""
        self.observer.stop()

    def load_file(self, path):
        """
        Loads or reloads a module, given its file path.
        :type path: str
        """
        # call_soon_threadsafe doesn't support kwargs, so use a lambda
        self.bot.loop.call_soon_threadsafe(
            lambda: asyncio.async(self.bot.plugin_manager.load_plugin(path), loop=self.bot.loop))


class PluginEventHandler(Trick):
    """
    :type loader: PluginLoader
    """

    def __init__(self, loader, *args, **kwargs):
        """
        :type loader: PluginLoader
        """
        super().__init__(*args, **kwargs)
        self.loader = loader

    def on_created(self, event):
        self.loader.load_file(event.src_path.decode())

    def on_modified(self, event):
        self.loader.load_file(event.src_path.decode())

    def on_moved(self, event):
        # only load if it's moved to a .py file
        if event.dest_path.endswith(b".py"):
            self.loader.load_file(event.dest_path.decode())
