import importlib
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
        self.plugin_path = os.path.abspath("plugins")
        self.bot = bot

        self.event_handler = PluginEventHandler(self, patterns=["*.py"])
        self.observer.schedule(self.event_handler, self.plugin_path, recursive=False)
        self.observer.start()

        self.load_all()

    def stop(self):
        """shuts down the plugin reloader"""
        self.observer.stop()

    def load_all(self):
        """runs load_file() on all python files in the plugins folder"""
        files = set(glob.glob(os.path.join(self.plugin_path, '*.py')))
        for f in files:
            self.load_file(f)

    def load_file(self, path):
        """loads (or reloads) all valid plugins from a specified file
        :type path: str
        """
        if isinstance(path, bytes):
            # makes sure that the filename is a 'str' object, not a 'bytes' object
            path = path.decode()
        filepath = os.path.abspath(path)
        filename = os.path.basename(path)
        title_and_extension = os.path.splitext(filename)

        if title_and_extension[1] != ".py":
            # ignore non-python plugin files
            return
        self.unload_file(filepath)

        try:
            plugin_module = importlib.import_module("plugins.{}".format(title_and_extension[0]))
        except:
            self.bot.logger.exception("Error loading {}:".format(filename))
            return

        self.bot.plugin_manager.load_plugin(filepath, plugin_module)

    def unload_file(self, path):
        """unloads all loaded plugins from a specified file
        :type path: str
        """
        filepath = os.path.abspath(path)
        filename = os.path.basename(path)
        if isinstance(filename, bytes):
            # makes sure that the filename is a 'str' object, not a 'bytes' object
            filename = filename.decode()
        title_and_extension = os.path.splitext(filename)

        if title_and_extension[1] != ".py":
            # ignore non-python plugin files
            return

        # stop all currently running instances of the plugins from this file
        for running_plugin, handler in list(self.bot.threads.items()):
            if running_plugin.fileplugin.filepath == filepath:
                handler.stop()
                del self.bot.threads[running_plugin]

        # unload the plugin
        self.bot.plugin_manager.unload_plugin(filepath)


class PluginEventHandler(Trick):
    def __init__(self, loader, *args, **kwargs):
        self.loader = loader
        Trick.__init__(self, *args, **kwargs)

    def on_created(self, event):
        self.loader.load_file(event.src_path)

    def on_deleted(self, event):
        self.loader.unload_file(event.src_path)

    def on_modified(self, event):
        self.loader.load_file(event.src_path)

    def on_moved(self, event):
        self.loader.unload_file(event.src_path)
        self.loader.load_file(event.dest_path)
