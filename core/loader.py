import os
import glob

from watchdog.observers import Observer
from watchdog.tricks import Trick


class PluginLoader(object):
    def __init__(self, bot):
        """
        :type bot: core.bot.CloudBot
        """
        self.observer = Observer()
        self.module_path = os.path.abspath("modules")
        self.bot = bot

        self.event_handler = PluginEventHandler(self, patterns=["*.py"])
        self.observer.schedule(self.event_handler, self.module_path, recursive=False)
        self.observer.start()

        self.load_all()

    def stop(self):
        """shuts down the plugin reloader"""
        self.observer.stop()

    def load_all(self):
        """
        Loads all modules in the module directory.
        """
        self.bot.plugin_manager.load_all(glob.iglob(os.path.join(self.module_path, '*.py')))

    def load_file(self, path):
        """
        Loads a module, given its file path.
        :type path: str
        """
        self.bot.plugin_manager.load_module(path)

    def unload_file(self, path):
        """
        Unloads a module, given its file path.
        :type path: str
        """
        self.bot.plugin_manager.unload_module(path)


class PluginEventHandler(Trick):
    def __init__(self, loader, *args, **kwargs):
        """
        :type loader: PluginLoader
        """
        self.loader = loader
        Trick.__init__(self, *args, **kwargs)

    def on_created(self, event):
        self.loader.load_file(event.src_path.decode())

    def on_deleted(self, event):
        self.loader.unload_file(event.src_path.decode())

    def on_modified(self, event):
        self.loader.load_file(event.src_path.decode())

    def on_moved(self, event):
        if event.src_path.endswith(b".py"):
            # if it's moved from a non-.py file, don't unload it
            self.loader.unload_file(event.src_path.decode())
        if event.dest_path.endswith(b".py"):
            # if it's moved to a non-.py file, don't load it
            self.loader.load_file(event.dest_path.decode())
