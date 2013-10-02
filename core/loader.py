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
        self.observer.stop()


    def load_all(self):
        files = set(glob.glob(os.path.join(self.path, '*.py')))
        for f in files:
            self.load_file(f, loaded_all=True)
        self.rebuild()


    def load_file(self, path, loaded_all=False):
        filename = os.path.basename(path)

        try:
            code = compile(open(path, 'U').read(), filename, 'exec')
            namespace = {}
            eval(code, namespace)
        except Exception:
            traceback.print_exc()
            return

        # remove plugins already loaded from this filename
        for name, data in self.bot.plugins.iteritems():
            self.bot.plugins[name] = [x for x in data
                                if x[0]._filename != filename]

        for func, handler in list(self.bot.threads.iteritems()):
            if func._filename == filename:
                handler.stop()
                del self.bot.threads[func]

        for obj in namespace.itervalues():
            if hasattr(obj, '_hook'):  # check for magic
                if obj._thread:
                    self.bot.threads[obj] = main.Handler(self.bot, obj)

                for type, data in obj._hook:
                    self.bot.plugins[type] += [data]
                    if not loaded_all:
                        self.bot.logger.info("Loaded plugin: {} ({})".format(format_plug(data), type))

        if not loaded_all:
            self.rebuild()


    def unload_file(self, path):
        filename = os.path.basename(path)
        self.bot.logger.info("Unloading plugins from: {}".format(filename))

        for plugin_type, plugins in self.bot.plugins.iteritems():
            self.bot.plugins[plugin_type] = [x for x in plugins if x[0]._filename != filename]

        for func, handler in list(self.bot.threads.iteritems()):
            if func._filename == filename:
                main.handler.stop()
                del self.bot.threads[func]


    def rebuild(self):
        self.bot.commands = {}
        for plug in self.bot.plugins['command']:
            name = plug[1]['name'].lower()
            if not re.match(r'^\w+$', name):
                print '### ERROR: invalid command name "{}" ({})'.format(name, format_plug(plug))
                continue
            if name in self.bot.commands:
                print "### ERROR: command '{}' already registered ({}, {})".format(name,
                                                                                   format_plug(self.bot.commands[name]),
                                                                                   format_plug(plug))
                continue
            self.bot.commands[name] = plug

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
