import os
import re
import glob
import collections
import traceback

from watchdog.observers import Observer
from watchdog.tricks import Trick

from core import main


def make_signature(f):
    return f.func_code.co_filename, f.func_name, f.func_code.co_firstlineno


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
        """loads plugins from all files in the plugins folder"""
        files = set(glob.glob(os.path.join(self.path, '*.py')))
        for f in files:
            self.load_file(f, loaded_all=True)
        self.rebuild()


    def load_file(self, path, loaded_all=False):
        """loads (or reloads) all valid plugins from a specified file"""
        filename = os.path.basename(path)
        title = os.path.splitext(filename)[0]

        disabled = self.bot.config.get('disabled_plugins', [])
        if title in disabled:
            self.bot.logger.info("Did not load plugins from: {} (plugin disabled)".format(filename))
            return None

        # compile the file and eval it in a namespace
        try:
            code = compile(open(path, 'U').read(), filename, 'exec')
            namespace = {}
            eval(code, namespace)
        except Exception:
            self.bot.logger.error("Error compiling {}:".format(filename))
            self.bot.logger.error(traceback.format_exc())
            return

        # remove plugins already loaded from this file
        for name, data in self.bot.plugins.iteritems():
            self.bot.plugins[name] = [x for x in data
                                if x[0]._filename != filename]

        # stop all currently running instances of the plugins from this file
        for func, handler in list(self.bot.threads.iteritems()):
            if func._filename == filename:
                handler.stop()
                del self.bot.threads[func]

        # find objects with hooks in the plugin namespace
        # TODO: kill it with fire, kill it all
        for obj in namespace.itervalues():
            if hasattr(obj, '_hook'):  # check for magic
                if obj._thread:
                    # TODO: pretty sure this is broken
                    self.bot.threads[obj] = main.Handler(self.bot, obj)

                for type, data in obj._hook:
                    # add plugin to the plugin list
                    self.bot.plugins[type] += [data]
                    if not loaded_all:
                        self.bot.logger.info("Loaded plugin: {} ({})".format(format_plug(data), type))

        # do a rebuild, unless the bot is loading all plugins (rebuild happens after load_all)
        if not loaded_all:
            self.rebuild()


    def unload_file(self, path):
        """unloads all loaded plugins from a specified file"""
        filename = os.path.basename(path)
        self.bot.logger.info("Unloading plugins from: {}".format(filename))

        # remove plugins loaded from this file
        for plugin_type, plugins in self.bot.plugins.iteritems():
            self.bot.plugins[plugin_type] = [x for x in plugins if x[0]._filename != filename]

        # stop all currently running instances of the plugins from this file
        for func, handler in list(self.bot.threads.iteritems()):
            if func._filename == filename:
                main.handler.stop()
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
                self.bot.logger.error('Command already registered: "{}" ({}, {})'.format(name,
                                                                                   format_plug(self.bot.commands[name]),
                                                                                   format_plug(plugin)))
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
