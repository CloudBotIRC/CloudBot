import importlib
import os
import glob
import imp

from watchdog.observers import Observer
from watchdog.tricks import Trick


class PluginLoader(object):
    def __init__(self, bot):
        """
        :type bot: core.bot.CloudBot
        """
        self.observer = Observer()
        self.module_path = os.path.abspath("modules")
        print(self.module_path)
        self.bot = bot

        self.event_handler = PluginEventHandler(self, patterns=["*.py"])
        self.observer.schedule(self.event_handler, self.module_path, recursive=False)
        self.observer.start()

        self.load_all()

    def stop(self):
        """shuts down the plugin reloader"""
        self.observer.stop()

    def load_all(self):
        """runs load_file() on all python files in the modules folder"""
        files = set(glob.glob(os.path.join(self.module_path, '*.py')))
        for f in files:
            self.load_file(f)

    def load_file(self, path):
        """
        Loads a module, given its file path.
        :type path: str
        """
        if isinstance(path, bytes):
            path = path.decode()

        file_path = os.path.abspath(path)
        file_name = os.path.basename(path)
        split_path = os.path.splitext(file_name)

        if split_path[1] != ".py":
            # ignore non-python plugin files
            return
        reload = self.unload_file(file_path)

        module_name = "modules.{}".format(split_path[0])
        try:
            module = importlib.import_module(module_name)
            if reload:
                # if this plugin was loaded before, reload it
                # this statement has to come after re-importing it, because we don't actually have a module object
                imp.reload(module)
        except Exception:
            self.bot.logger.exception("Error loading {}:".format(file_name))
            return


        self.bot.plugin_manager.load_module(file_path, module)

    def unload_file(self, path):
        """
        Unloads a module, given its file path.

        Returns True if the module was unloaded, False if the module wasn't loaded in the first place.
        :type path: str
        :rtype: bool
        """
        if isinstance(path, bytes):
            path = path.decode()

        file_path = os.path.abspath(path)
        file_name = os.path.basename(path)
        title_and_extension = os.path.splitext(file_name)

        if title_and_extension[1] != ".py":
            # ignore non-python plugin files
            return False

        # stop all currently running instances of the modules from this file
        for running_plugin, handler in list(self.bot.threads.items()):
            if running_plugin.module.file_path == file_path:
                handler.stop()
                del self.bot.threads[running_plugin]

        # unload the plugin
        return self.bot.plugin_manager.unload_module(file_path)


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
