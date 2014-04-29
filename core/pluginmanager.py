import imp
import importlib
import os
import re

import sqlalchemy

from core import main
from util import hook, botvars


def find_hooks(parent, code):
    """
    :type parent: Module
    :type code: object
    :rtype: (list[CommandPlugin], list[RegexPlugin], list[EventPlugin], list[SievePlugin], list[OnLoadPlugin])
    """
    commands = []
    regexes = []
    events = []
    sieves = []
    run_on_load = []
    type_lists = {"command": commands, "regex": regexes, "event": events, "sieve": sieves, "onload": run_on_load}
    for name, func in code.__dict__.items():
        if hasattr(func, "_cloudbot_hook"):
            # if it has cloudbot hook
            func_hooks = func._cloudbot_hook
            for hook_type, func_hook in func_hooks.items():
                assert func_hook.function == func  # make sure this is the right function

                type_lists[hook_type].append(_hook_name_to_plugin[hook_type](parent, func_hook))

    return commands, regexes, events, sieves, run_on_load


def find_tables(code):
    """
    :type parent: Module
    :type code: object
    :rtype: list[sqlalchemy.Table]
    """
    tables = []
    for name, obj in code.__dict__.items():
        if isinstance(obj, sqlalchemy.Table) and obj.metadata == botvars.metadata:
            # if it's a Table, and it's using our metadata, append it to the list
            tables.append(obj)

    return tables


class PluginManager:
    """
    PluginManager is the core of CloudBot plugin loading.

    PluginManager loads Modules, and adds their Plugins to easy-access dicts/lists.

    Each Module represents a file, and loads plugins onto itself using find_hooks.

    Plugins are the lowest level of abstraction in this class. There are four different plugin types:
    - CommandPlugin is for bot commands
    - EventPlugin hooks onto bot 'events'
    - RegexPlugin loads a regex parameter, and executes on input lines which match the regex
    - SievePlugin is a catch-all sieve, which all other plugins go through before being executed.

    :type bot: core.bot.CloudBot
    :type modules: dict[str, Module]
    :type commands: dict[str, CommandPlugin]
    :type events: dict[str, list[EventPlugin]]
    :type catch_all_events: list[EventPlugin]
    :type regex_plugins: list[(re.__Regex, RegexPlugin)]
    :type sieves: list[SievePlugin]
    """

    def __init__(self, bot):
        """
        Creates a new PluginManager. You generally only need to do this from inside core.bot.CloudBot
        :type bot: core.bot.CloudBot
        """
        self.bot = bot

        self.modules = {}
        self.commands = {}
        self.events = {}
        self.catch_all_events = []
        self.regex_plugins = []
        self.sieves = []

    def load_module(self, path):
        """
        Loads a module from the given path and module object, then registers all plugins from that module.

        This function checks whether the module is disabled in "disabled_plugins".

        :type path: str
        """
        file_path = os.path.abspath(path)
        file_name = os.path.basename(path)
        title = os.path.splitext(file_name)[0]
        if "disabled_plugins" in self.bot.config and title in self.bot.config['disabled_plugins']:
            self.bot.logger.info("Not loading module {}: module disabled".format(file_name))
            return

        existed = self.unload_module(file_path)

        module_name = "modules.{}".format(title)
        try:
            python_module = importlib.import_module(module_name)
            if existed:
                # if this plugin was loaded before, reload it
                # this statement has to come after re-importing it, because we don't actually have a module object
                # use imp.reload instead of importlib.reload, to remain compatible with python 3.2
                imp.reload(python_module)
        except Exception:
            self.bot.logger.exception("Error loading {}:".format(file_name))
            return

        module = Module(file_path, file_name, title, python_module)

        self.register_plugins(module)

    def unload_module(self, path):
        """
        Unloads the module from the given path, unloading all plugins from the module.

        Returns True if the module was unloaded, False if the module wasn't loaded in the first place.

        :type path: str
        :rtype: bool
        """
        file_name = os.path.basename(path)
        title = os.path.splitext(file_name)[0]
        if "disabled_plugins" in self.bot.config and title in self.bot.config['disabled_plugins']:
            # this plugin hasn't been loaded, so no need to unload it
            return False

        # stop all currently running instances of the modules from this file
        for running_plugin, handler in list(self.bot.threads.items()):
            if running_plugin.module.file_name == file_name:
                handler.stop()
                del self.bot.threads[running_plugin]

        return self.unregister_plugins(file_name, ignore_not_registered=True)

    def register_plugins(self, module, check_if_exists=True):
        """
        Registers all plugins in a given module

        :type module: Module
        :type check_if_exists: bool
        """
        if check_if_exists and module.file_name in self.modules:
            self.unregister_plugins(module.file_name)

        # create database tables
        module.create_tables(self.bot)

        # run onload hooks
        for onload_plugin in module.run_on_load:
            success = main.run(self.bot, onload_plugin, main.Input(bot=self.bot))
            if not success:
                self.bot.logger.warning("Not registering module {}: module onload hook errored".format(module.title))
                return

        self.modules[module.file_name] = module

        # register commands
        for command in module.commands:
            for alias in command.aliases:
                if alias in self.commands:
                    self.bot.logger.warning(
                        "Plugin {} attempted to register command {} which was already registered by {}. "
                        "Ignoring new assignment.".format(module.title, alias, self.commands[alias].module.title))
                else:
                    self.commands[alias] = command
            self.log_plugin(command)

        # register events
        for event_plugin in module.events:
            if event_plugin.is_catch_all():
                self.catch_all_events.append(event_plugin)
            else:
                for event_name in event_plugin.events:
                    if event_name in self.events:
                        self.events[event_name].append(event_plugin)
                    else:
                        self.events[event_name] = [event_plugin]
            self.log_plugin(event_plugin)

        # register regexps
        for regex_plugin in module.regexes:
            for regex_match in regex_plugin.regexes:
                self.regex_plugins.append((regex_match, regex_plugin))
            self.log_plugin(regex_plugin)

        # register sieves
        for sieve_plugin in module.sieves:
            self.sieves.append(sieve_plugin)
            self.log_plugin(sieve_plugin)

    def unregister_plugins(self, module, ignore_not_registered=False):
        """
        Unregisters all plugins from a given module.

        Returns True if all plugins in the module were unloaded, False if the ignore_not_registered and the module
        wasn't registered in the first place. Throws an exception if ignore_not_registered is false and it wasn't loaded
        in the first place.

        :param module: Module to unregister plugins from, or str to lookup via file_name and then unload.
        :type module: Module | str

        """
        if isinstance(module, str):
            if ignore_not_registered:
                if not module in self.modules:
                    return False
            else:
                assert module in self.modules
            module = self.modules[module]
        else:
            assert isinstance(module, Module)
            if ignore_not_registered:
                if not module.file_name in self.modules:
                    return False
            else:
                assert module.file_name in self.modules
            assert self.modules[module.file_name] is module
            # we don't want to be unload a module which isn't loaded

        # unregister commands
        for command in module.commands:
            for alias in command.aliases:
                if alias in self.commands and self.commands[alias] == command:
                    # we need to make sure that there wasn't a conflict, and another module got this command.
                    del self.commands[alias]

        # unregister events
        for event_plugin in module.events:
            if event_plugin.is_catch_all():
                self.catch_all_events.remove(event_plugin)
            else:
                for event_name in event_plugin.events:
                    assert event_name in self.events  # this can't be not true
                    self.events[event_name].remove(event_plugin)

        # unregister regexps
        for regex_plugin in module.regexes:
            for regex_match in regex_plugin.regexes:
                self.regex_plugins.remove((regex_match, regex_plugin))

        # unregister sieves
        for sieve_plugin in module.sieves:
            self.sieves.remove(sieve_plugin)

        # unregister databases
        module.unregister_tables(self.bot)

        # remove last reference to module
        del self.modules[module.file_name]

        # this will remove all reverences to the plugins and functions themselves if anyone still has an old Module or
        # Plugin object
        for plugin in module.commands + module.regexes + module.events + module.sieves:
            del plugin.function
        del module.commands[:]
        del module.regexes[:]
        del module.events[:]
        del module.sieves[:]
        self.bot.logger.info("Unloaded all plugins from {}".format(module.title))

        return True

    def log_plugin(self, plugin):
        """
        Logs registering this plugin.
        :type plugin: Plugin
        """
        self.bot.logger.info("Loaded {}".format(plugin))
        self.bot.logger.debug("Loaded {}".format(repr(plugin)))


class Module:
    """
    Each Module represents a file, and loads plugins onto itself using find_hooks.

    :type file_path: str
    :type file_name: str
    :type title: str
    :type commands: list[CommandPlugin]
    :type regexes: list[RegexPlugin]
    :type events: list[EventPlugin]
    :type sieves: list[SievePlugin]
    :type tables: list[sqlalchemy.Table]
    """

    def __init__(self, filepath, filename, title, code):
        """
        :type filepath: str
        :type filename: str
        :type code: object
        """
        self.file_path = filepath
        self.file_name = filename
        self.title = title
        self.commands, self.regexes, self.events, self.sieves, self.run_on_load = find_hooks(self, code)
        # we need to find tables for each module so that they can be unloaded from the global metadata when the
        # plugin is reloaded
        self.tables = find_tables(code)

    def create_tables(self, bot):
        """
        Creates all sqlalchemy Tables that are registered in this plugin
        :type bot: core.bot.CloudBot
        """
        if self.tables:
            # if there are any tables

            bot.logger.info("Registering tables for {}".format(self.title))

            for table in self.tables:
                if not table.exists(bot.db_engine):
                    table.create(bot.db_engine)

    def unregister_tables(self, bot):
        """
        Unregisters all sqlalchemy Tables registered to the global metadata by this module
        :type bot: core.bot.CloudBot
        """
        if self.tables:
            # if there are any tables
            bot.logger.info("Unregistering tables for {}".format(self.title))

            for table in self.tables:
                bot.db_metadata.remove(table)


class Plugin:
    """
    Each plugin is specific to one function. This class is never used by iself, it's always extended by CommandPlugin,
    EventPlugin, RegexPlugin, or SievePlugin
    :type type; str
    :type module: Module
    :type function: function
    :type function_name: str
    :type args: dict[str, unknown]
    """

    def __init__(self, plugin_type, module, func_hook):
        """
        :type plugin_type: str
        :type module: Module
        :type func_hook: hook._Hook
        """
        self.type = plugin_type
        self.module = module
        self.function = func_hook.function
        self.function_name = self.function.__name__
        self.args = func_hook.kwargs

    def __repr__(self):
        return "type: {}, module: {}, args: {}".format(self.type, self.module.file_name, self.args)


class CommandPlugin(Plugin):
    """
    :type name: str
    :type aliases: list[str]
    :type doc: str
    """

    def __init__(self, module, cmd_hook):
        """
        :type module: Module
        :type cmd_hook: hook._CommandHook
        """
        Plugin.__init__(self, "command", module, cmd_hook)

        # make sure that autohelp and permissions are set
        if not "autohelp" in self.args:
            self.args["autohelp"] = True
        if not "permissions" in self.args:
            self.args["permissions"] = []

        self.name = cmd_hook.main_alias
        self.aliases = list(cmd_hook.aliases)  # turn the set into a list
        self.aliases.remove(self.name)
        self.aliases.insert(0, self.name)  # make sure the name, or 'main alias' is in position 0
        self.doc = cmd_hook.doc

    def __repr__(self):
        return "CommandPlugin[name: {}, aliases: {}, {}]".format(self.name, self.aliases[1:], Plugin.__repr__(self))

    def __str__(self):
        return "command {} from {}".format("/".join(self.aliases), self.module.file_name)


class RegexPlugin(Plugin):
    """
    :type regexes: set[re.__Regex]
    """

    def __init__(self, module, regex_hook):
        """
        :type module: Module
        :type regex_hook: hook._RegexHook
        """
        Plugin.__init__(self, "regex", module, regex_hook)
        self.regexes = regex_hook.regexes

    def __repr__(self):
        return "RegexPlugin[regexes: {}, {}]".format([regex.pattern for regex in self.regexes], Plugin.__repr__(self))

    def __str__(self):
        return "regex {} from {}".format(self.function_name, self.module.file_name)


class EventPlugin(Plugin):
    """
    :type events: set[str]
    """

    def __init__(self, module, event_hook):
        """
        :type module: Module
        :type event_hook: hook._EventHook
        """
        Plugin.__init__(self, "event", module, event_hook)

        if not "run_sync" in self.args:
            self.args["run_sync"] = False

        self.events = event_hook.events

    def is_catch_all(self):
        return "*" in self.events

    def __repr__(self):
        return "EventPlugin[events: {}, {}]".format(list(self.events), Plugin.__repr__(self))

    def __str__(self):
        return "events {} ({}) from {}".format(self.function_name, ",".join(self.events), self.module.file_name)


class SievePlugin(Plugin):
    def __init__(self, module, sieve_hook):
        """
        :type module: Module
        :type sieve_hook: hook._SieveHook
        """
        Plugin.__init__(self, "sieve", module, sieve_hook)

    def __repr__(self):
        return "SievePlugin[{}]".format(Plugin.__repr__(self))

    def __str__(self):
        return "sieve {} from {}".format(self.function_name, self.module.file_name)


class OnLoadPlugin(Plugin):
    def __init__(self, module, on_load_hook):
        """
        :type module: Module
        :type on_load_hook: hook._OnLoadHook
        """
        Plugin.__init__(self, "onload", module, on_load_hook)

    def __repr__(self):
        return "OnLoadPlugin[{}]".format(Plugin.__repr__(self))

    def __str__(self):
        return "onload {} from {}".format(self.function_name, self.module.file_name)


_hook_name_to_plugin = {
    "command": CommandPlugin,
    "regex": RegexPlugin,
    "event": EventPlugin,
    "sieve": SievePlugin,
    "onload": OnLoadPlugin
}
