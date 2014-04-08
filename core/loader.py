import os
import re
import glob
import collections

from watchdog.observers import Observer
from watchdog.tricks import Trick

from core import main


def make_signature(f):
    return f.__code__.co_filename, f.__name__, f.__code__.co_firstlineno


def format_plug(plug, kind='', lpad=0):
    out = ' ' * lpad + '{}:{}:{}'.format(*make_signature(plug[0]))
    if kind == 'command':
        out += ' ' * (50 - len(out)) + plug[1]['name']

    if kind == 'event':
        out += ' ' * (50 - len(out)) + ', '.join(plug[1]['events'])

    if kind == 'regex':
        out += ' ' * (50 - len(out)) + plug[1]['regex']

    return out


class PluginLoader(object):
    def __init__(self, bot):
        """
        :type bot: core.bot.CloudBot
        """
        self.observer = Observer()
        self.path = os.path.abspath("plugins")
        self.bot = bot

        self.event_handler = PluginEventHandler(self, patterns=["*.py"])
        self.observer.schedule(self.event_handler, self.path, recursive=False)
        self.observer.start()

        self.load_all()

    def stop(self):
        """shuts down the plugin reloader"""
        self.observer.stop()

    def load_all(self):
        """runs load_file() on all python files in the plugins folder"""
        files = set(glob.glob(os.path.join(self.path, '*.py')))
        for f in files:
            self.load_file(f, rebuild=True)
        self.rebuild()

    def load_file(self, path, rebuild=False):
        """loads (or reloads) all valid plugins from a specified file
        :type path: str
        :type rebuild: bool
        """
        filename = os.path.basename(path)
        if isinstance(filename, bytes):
            # makes sure that the filename is a 'str' object, not a 'bytes' object
            filename = filename.decode()
        file_split = os.path.splitext(filename)
        title = file_split[0]
        extension = file_split[1]
        if extension != ".py":
            # ignore non-python plugin files
            return

        disabled = self.bot.config.get('disabled_plugins', [])
        if title in disabled:
            self.bot.logger.info("Not loading plugin {}: plugin disabled".format(filename))
            return

        # compile the file and eval it in a namespace
        try:
            code = compile(open(path, 'U').read(), filename, 'exec')
            namespace = {}
            eval(code, namespace)
        except Exception:
            self.bot.logger.exception("Error compiling {}:".format(filename))
            return

        # remove plugins already loaded from this file
        for plug_type, data in self.bot.plugins.items():
            self.bot.plugins[plug_type] = [x for x in data
                                           if x[0]._filename != filename]

        # stop all currently running instances of the plugins from this file
        for func, handler in list(self.bot.threads.items()):
            if func._filename == filename:
                handler.stop()
                del self.bot.threads[func]

        # find objects with hooks in the plugin namespace
        # TODO: kill it with fire, kill it all
        for obj in namespace.values():
            if hasattr(obj, '_hook'):  # check for magic
                if obj._thread:
                    self.bot.threads[obj] = main.Handler(self.bot, obj)
                for plug_type, data in obj._hook:
                    # add plugin to the plugin list
                    self.bot.plugins[plug_type] += [data]
                    self.bot.logger.info("Loaded plugin: {} ({})".format(format_plug(data), plug_type))

        # do a rebuild, unless the bot is loading all plugins (rebuild happens after load_all)
        if not rebuild:
            self.rebuild()

    def unload_file(self, path):
        """unloads all loaded plugins from a specified file
        :type path: str
        """
        filename = os.path.basename(path)
        if isinstance(filename, bytes):
            # makes sure that the filename is a 'str' object, not a 'bytes' object
            filename = filename.decode()
        file_split = os.path.splitext(filename)
        title = file_split[0]
        extension = file_split[1]
        if extension != ".py":
            # ignore non-python plugin files
            return

        disabled = self.bot.config.get('disabled_plugins', [])
        if title in disabled:
            # this plugin hasn't been loaded, so no need to unload it
            return

        self.bot.logger.info("Unloading plugins from: {}".format(filename))

        # remove plugins loaded from this file
        for plugin_type, plugins in self.bot.plugins.items():
            self.bot.plugins[plugin_type] = [x for x in plugins if x[0]._filename != filename]

        # stop all currently running instances of the plugins from this file
        for func, handler in list(self.bot.threads.items()):
            if func._filename == filename:
                handler.stop()
                del self.bot.threads[func]

        self.rebuild()

    def rebuild(self):
        """rebuilds the cloudbot command and event hook lists"""
        self.bot.commands = {}
        for plugin in self.bot.plugins['command']:
            name = plugin[1]['name'].lower()
            if not re.match(r'^\w+$', name):
                self.bot.logger.error('Invalid command name: "{}" ({})'.format(name, format_plug(plugin)))
                continue
            if name in self.bot.commands:
                self.bot.logger.error('Command already registered: "{}" ({}, {})'
                                      .format(name, format_plug(self.bot.commands[name]), format_plug(plugin)))
                continue
            self.bot.commands[name] = plugin

        self.bot.events = collections.defaultdict(list)
        for func, args in self.bot.plugins['event']:
            for event in args['events']:
                self.bot.events[event].append((func, args))


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
