import asyncio
import glob
import importlib
import inspect
import logging
import os
import re

import sqlalchemy

from . import main
from ..util import botvars


def find_hooks(parent, module):
    """
    :type parent: Plugin
    :type module: object
    :rtype: (list[CommandHook], list[RegexHook], list[RawHook], list[SieveHook], list[OnloadHook])
    """
    # set the loaded flag
    module._cloudbot_loaded = True
    command = []
    regex = []
    raw = []
    sieve = []
    onload = []
    type_lists = {"command": command, "regex": regex, "raw": raw, "sieve": sieve, "onload": onload}
    for name, func in module.__dict__.items():
        if hasattr(func, "_cloudbot_hook"):
            # if it has cloudbot hook
            func_hooks = func._cloudbot_hook
            for hook_type, func_hook in func_hooks.items():
                type_lists[hook_type].append(_hook_name_to_plugin[hook_type](parent, func_hook))

            # delete the hook to free memory
            del func._cloudbot_hook

    return command, regex, raw, sieve, onload


def find_tables(code):
    """
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

    PluginManager loads Plugins, and adds their Hooks to easy-access dicts/lists.

    Each Plugin represents a file, and loads hooks onto itself using find_hooks.

    Plugins are the lowest level of abstraction in this class. There are four different plugin types:
    - CommandPlugin is for bot commands
    - RawPlugin hooks onto raw irc lines
    - RegexPlugin loads a regex parameter, and executes on input lines which match the regex
    - SievePlugin is a catch-all sieve, which all other plugins go through before being executed.

    :type bot: cloudbot.core.bot.CloudBot
    :type plugins: dict[str, Plugin]
    :type commands: dict[str, CommandHook]
    :type raw_triggers: dict[str, list[RawHook]]
    :type catch_all_events: list[RawHook]
    :type regex_hooks: list[(re.__Regex, RegexHook)]
    :type sieves: list[SieveHook]
    """

    def __init__(self, bot):
        """
        Creates a new PluginManager. You generally only need to do this from inside core.bot.CloudBot
        :type bot: cloudbot.core.bot.CloudBot
        """
        self.bot = bot

        self.plugins = {}
        self.commands = {}
        self.raw_triggers = {}
        self.catch_all_events = []
        self.regex_hooks = []
        self.sieves = []

    @asyncio.coroutine
    def load_all(self, plugin_dir):
        """
        Load a plugin from each *.py file in the given directory.

        Won't load any plugins listed in "disabled_plugins".

        :type plugin_dir: str
        """
        path_list = glob.iglob(os.path.join(plugin_dir, '*.py'))
        # Load plugins asynchronously :O
        yield from asyncio.gather(*[self.load_plugin(path) for path in path_list], loop=self.bot.loop)

    @asyncio.coroutine
    def load_plugin(self, path):
        """
        Loads a plugin from the given path and plugin object, then registers all hooks from that plugin.

        Won't load any plugins listed in "disabled_plugins".

        :type path: str
        """
        file_path = os.path.abspath(path)
        file_name = os.path.basename(path)
        title = os.path.splitext(file_name)[0]
        if "disabled_plugins" in self.bot.config and title in self.bot.config['disabled_plugins']:
            self.bot.logger.info("Not loading plugin {}: plugin disabled".format(file_name))
            return

        # make sure to unload the previously loaded plugin from this path, if it was loaded.
        if file_name in self.plugins:
            yield from self._unload(file_path)

        module_name = "modules.{}".format(title)
        try:
            plugin_module = importlib.import_module(module_name)
            # if this plugin was loaded before, reload it
            if hasattr(plugin_module, "_cloudbot_loaded"):
                importlib.reload(plugin_module)
        except Exception:
            self.bot.logger.exception("Error loading {}:".format(file_name))
            return

        # create the plugin
        plugin = Plugin(file_path, file_name, title, plugin_module)

        # proceed to register hooks

        # create database tables
        plugin.create_tables(self.bot)

        # run onload hooks
        for onload_hook in plugin.run_on_load:
            success = yield from main.dispatch(self.bot, onload_hook, main.Input(bot=self.bot))
            if not success:
                self.bot.logger.warning(
                    "Not registering hooks from plugin {}: onload hook errored".format(plugin.title))

                # unregister databases
                plugin.unregister_tables(self.bot)
                return

        self.plugins[plugin.file_name] = plugin

        # register commands
        for command_hook in plugin.commands:
            for alias in command_hook.aliases:
                if alias in self.commands:
                    self.bot.logger.warning(
                        "Plugin {} attempted to register command {} which was already registered by {}. "
                        "Ignoring new assignment.".format(plugin.title, alias, self.commands[alias].plugin.title))
                else:
                    self.commands[alias] = command_hook
            self._log_hook(command_hook)

        # register events
        for raw_hook in plugin.raw_hooks:
            if raw_hook.is_catch_all():
                self.catch_all_events.append(raw_hook)
            else:
                for trigger in raw_hook.triggers:
                    if trigger in self.raw_triggers:
                        self.raw_triggers[trigger].append(raw_hook)
                    else:
                        self.raw_triggers[trigger] = [raw_hook]
            self._log_hook(raw_hook)

        # register regexps
        for regex_hook in plugin.regexes:
            for regex_match in regex_hook.regexes:
                self.regex_hooks.append((regex_match, regex_hook))
            self._log_hook(regex_hook)

        # register sieves
        for sieve_hook in plugin.sieves:
            self.sieves.append(sieve_hook)
            self._log_hook(sieve_hook)

        # we don't need this anymore
        del plugin.run_on_load

    @asyncio.coroutine
    def _unload(self, path):
        """
        Unloads the plugin from the given path, unregistering all hooks from the plugin.

        Returns True if the plugin was unloaded, False if the plugin wasn't loaded in the first place.

        :type path: str
        :rtype: bool
        """
        file_name = os.path.basename(path)
        title = os.path.splitext(file_name)[0]
        if "disabled_plugins" in self.bot.config and title in self.bot.config['disabled_plugins']:
            # this plugin hasn't been loaded, so no need to unload it
            return False

        # stop all currently running instances of hooks from this plugin
        for key, handler in list(self.bot.handlers.items()):
            _title, function_name = key
            if _title == title:
                yield from handler.stop()

        # make sure this plugin is actually loaded
        if not file_name in self.plugins:
            return False

        # get the loaded plugin
        plugin = self.plugins[file_name]

        # unregister commands
        for command_hook in plugin.commands:
            for alias in command_hook.aliases:
                if alias in self.commands and self.commands[alias] == command_hook:
                    # we need to make sure that there wasn't a conflict, so we don't delete another plugin's command
                    del self.commands[alias]

        # unregister events
        for raw_hook in plugin.raw_hooks:
            if raw_hook.is_catch_all():
                self.catch_all_events.remove(raw_hook)
            else:
                for event_name in raw_hook.triggers:
                    assert event_name in self.raw_triggers  # this can't be not true
                    self.raw_triggers[event_name].remove(raw_hook)

        # unregister regexps
        for regex_hook in plugin.regexes:
            for regex_match in regex_hook.regexes:
                self.regex_hooks.remove((regex_match, regex_hook))

        # unregister sieves
        for sieve_hook in plugin.sieves:
            self.sieves.remove(sieve_hook)

        # unregister databases
        plugin.unregister_tables(self.bot)

        # remove last reference to plugin
        del self.plugins[plugin.file_name]

        self.bot.logger.info("Unloaded all plugins from {}".format(plugin.title))

        return True

    def _log_hook(self, hook):
        """
        Logs registering a given hook

        :type hook: Hook
        """
        self.bot.logger.info("Loaded {}".format(hook))
        self.bot.logger.debug("Loaded {}".format(repr(hook)))


class Plugin:
    """
    Each Plugin represents a plugin file, and contains loaded hooks.

    :type file_path: str
    :type file_name: str
    :type title: str
    :type commands: list[CommandHook]
    :type regexes: list[RegexHook]
    :type raw_hooks: list[RawHook]
    :type sieves: list[SieveHook]
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
        self.commands, self.regexes, self.raw_hooks, self.sieves, self.run_on_load = find_hooks(self, code)
        # we need to find tables for each plugin so that they can be unloaded from the global metadata when the
        # plugin is reloaded
        self.tables = find_tables(code)

    def create_tables(self, bot):
        """
        Creates all sqlalchemy Tables that are registered in this plugin

        :type bot: cloudbot.core.bot.CloudBot
        """
        if self.tables:
            # if there are any tables

            bot.logger.info("Registering tables for {}".format(self.title))

            for table in self.tables:
                if not table.exists(bot.db_engine):
                    table.create(bot.db_engine)

    def unregister_tables(self, bot):
        """
        Unregisters all sqlalchemy Tables registered to the global metadata by this plugin
        :type bot: cloudbot.core.bot.CloudBot
        """
        if self.tables:
            # if there are any tables
            bot.logger.info("Unregistering tables for {}".format(self.title))

            for table in self.tables:
                bot.db_metadata.remove(table)


class Hook:
    """
    Each hook is specific to one function. This class is never used by itself, rather extended.

    :type type; str
    :type plugin: Plugin
    :type function: callable
    :type function_name: str
    :type required_args: list[str]
    :type threaded: bool
    :type ignore_bots: bool
    :type permissions: list[str]
    :type single_thread: bool
    """

    def __init__(self, _type, plugin, func_hook, default_threaded=True):
        """
        :type _type: str
        :type plugin: Plugin
        :type func_hook: hook._Hook
        """
        self.type = _type
        self.plugin = plugin
        self.function = func_hook.function
        self.function_name = self.function.__name__

        self.required_args = inspect.getargspec(self.function)[0]
        if self.required_args is None:
            self.required_args = []

        if func_hook.kwargs.pop("threaded", default_threaded) and not asyncio.iscoroutine(self.function):
            self.threaded = True
        else:
            self.threaded = False
            if not asyncio.iscoroutine(self.function):
                self.function = asyncio.coroutine(self.function)

        self.ignore_bots = func_hook.kwargs.pop("ignorebots", False)
        self.permissions = func_hook.kwargs.pop("permissions", [])
        self.single_thread = func_hook.kwargs.pop("singlethread", False)

        if func_hook.kwargs:
            # we should have popped all the args, so warn if there are any left
            logging.getLogger("cloudbot").warning("Ignoring extra args {} from {}:{}".format(
                func_hook.kwargs, self.plugin.title, self.function_name))

    def __repr__(self):
        return "type: {}, plugin: {}, ignore_bots: {}, permissions: {}, single_thread: {}, threaded: {}".format(
            self.type, self.plugin.title, self.ignore_bots, self.permissions, self.single_thread, self.threaded
        )


class CommandHook(Hook):
    """
    :type name: str
    :type aliases: list[str]
    :type doc: str
    :type auto_help: bool
    """

    def __init__(self, plugin, cmd_hook):
        """
        :type plugin: Plugin
        :type cmd_hook: cloudbot.util.hook._CommandHook
        """
        self.auto_help = cmd_hook.kwargs.pop("autohelp", True)

        self.name = cmd_hook.main_alias
        self.aliases = list(cmd_hook.aliases)  # turn the set into a list
        self.aliases.remove(self.name)
        self.aliases.insert(0, self.name)  # make sure the name, or 'main alias' is in position 0
        self.doc = cmd_hook.doc

        super().__init__("command", plugin, cmd_hook)

    def __repr__(self):
        return "Command[name: {}, aliases: {}, {}]".format(self.name, self.aliases[1:], Hook.__repr__(self))

    def __str__(self):
        return "command {} from {}".format("/".join(self.aliases), self.plugin.file_name)


class RegexHook(Hook):
    """
    :type regexes: set[re.__Regex]
    """

    def __init__(self, plugin, regex_hook):
        """
        :type plugin: Plugin
        :type regex_hook: cloudbot.util.hook._RegexHook
        """
        self.regexes = regex_hook.regexes

        super().__init__("regex", plugin, regex_hook)

    def __repr__(self):
        return "Regex[regexes: {}, {}]".format([regex.pattern for regex in self.regexes],
                                               Hook.__repr__(self))

    def __str__(self):
        return "regex {} from {}".format(self.function_name, self.plugin.file_name)


class RawHook(Hook):
    """
    :type triggers: set[str]
    """

    def __init__(self, plugin, event_hook):
        """
        :type plugin: Plugin
        :type event_hook: cloudbot.util.hook._RawHook
        """
        super().__init__("raw", plugin, event_hook)

        self.triggers = event_hook.triggers

    def is_catch_all(self):
        return "*" in self.triggers

    def __repr__(self):
        return "Raw[events: {}, {}]".format(list(self.triggers), Hook.__repr__(self))

    def __str__(self):
        return "events {} ({}) from {}".format(self.function_name, ",".join(self.triggers), self.plugin.file_name)


class SieveHook(Hook):
    def __init__(self, plugin, sieve_hook):
        """
        :type plugin: Plugin
        :type sieve_hook: cloudbot.util.hook._SieveHook
        """
        # We don't want to thread sieves by default - this is retaining old behavior for compatibility
        super().__init__("sieve", plugin, sieve_hook, default_threaded=False)

    def __repr__(self):
        return "Sieve[{}]".format(Hook.__repr__(self))

    def __str__(self):
        return "sieve {} from {}".format(self.function_name, self.plugin.file_name)


class OnloadHook(Hook):
    def __init__(self, plugin, on_load_hook):
        """
        :type plugin: Plugin
        :type on_load_hook: cloudbot.util.hook._OnLoadHook
        """
        super().__init__("onload", plugin, on_load_hook)

    def __repr__(self):
        return "Onload[{}]".format(Hook.__repr__(self))

    def __str__(self):
        return "onload {} from {}".format(self.function_name, self.plugin.file_name)


_hook_name_to_plugin = {
    "command": CommandHook,
    "regex": RegexHook,
    "raw": RawHook,
    "sieve": SieveHook,
    "onload": OnloadHook
}
