import os
import re

from util import hook


def find_hooks(parent, code):
    """
    :type parent: FilePlugin
    :type code: object
    :rtype: (list[CommandPlugin], list[RegexPlugin], list[EventPlugin], list[SievePlugin])
    """
    commands = []
    regexes = []
    events = []
    sieves = []
    type_lists = {"command": commands, "regex": regexes, "event": events, "sieve": sieves}
    for name, func in code.__dict__.items():
        if hasattr(func, "_cloudbot_hook"):
            # if it has cloudbot hook
            func_hooks = func._cloudbot_hook
            for hook_type, func_hook in func_hooks.items():
                assert func_hook.function == func  # make sure this is the right function

                type_lists[hook_type].append(_hook_name_to_plugin[hook_type](parent, func_hook))

    return commands, regexes, events, sieves


def plugin_desc(plugin):
    if isinstance(plugin, CommandPlugin):
        return "command {}".format("/".join(plugin.aliases))
    elif isinstance(plugin, EventPlugin):
        return "events {} ({})".format(plugin.function_name, ",".join(plugin.events))
    elif isinstance(plugin, RegexPlugin):
        return "regex {}".format(plugin.function_name)
    elif isinstance(plugin, SievePlugin):
        return "sieve {}".format(plugin.function_name)


class PluginManager:
    """
    plugins is dict from file name to FilePlugin

    :type bot: core.bot.CloudBot
    :type plugins: dict[str, FilePlugin]
    :type commands: dict[str, CommandPlugin]
    :type events: dict[str, list[EventPlugin]]
    :type catch_all_events: list[EventPlugin]
    :type regex_plugins: list[(re.__Regex, RegexPlugin)]
    :type sieves: list[SievePlugin]
    """

    def __init__(self, bot):
        """
        :type bot: core.bot.CloudBot
        """
        self.bot = bot

        self.plugins = {}
        self.commands = {}
        self.events = {}
        self.catch_all_events = []
        self.regex_plugins = []
        self.sieves = []

    def register_plugins(self, plugins):
        """
        :param plugins: list of (file path, module)
        :type plugins: list[(str, object)]
        """
        for path, code in plugins:
            self.load_plugin(path, code)

    def load_plugin(self, path, code):
        """loads a plugin from the given path and code object
        :type path: str
        :type code: object
        """
        filepath = os.path.abspath(path)
        filename = os.path.basename(path)
        title = os.path.splitext(filename)[0]
        if "disabled_plugins" in self.bot.config and title in self.bot.config['disabled_plugins']:
            self.bot.logger.info("Not loading plugin {}: plugin disabled".format(filename))
            return
        plugin = FilePlugin(filepath, filename, title, code)
        self.register_plugin(plugin)

    def unload_plugin(self, path):
        """unloads a plugin from the given path

        """
        filename = os.path.basename(path)
        title = os.path.splitext(filename)[0]
        if "disabled_plugins" in self.bot.config and title in self.bot.config['disabled_plugins']:
            # this plugin hasn't been loaded, so no need to unload it
            return

        self.unregister_plugin(filename, ignore_not_registered=True)

    def register_plugin(self, plugin, check_if_exists=True):
        """
        :type plugin: FilePlugin
        """
        if check_if_exists and plugin.filename in self.plugins:
            self.unregister_plugin(plugin.filename)

        self.plugins[plugin.filename] = plugin

        # register commands
        for command in plugin.commands:
            for alias in command.aliases:
                if alias in self.commands:
                    self.bot.logger.warning("Plugin {} attempted to register command {} which was already registered "
                                            "by {}.Ignoring new assignment.",
                                            plugin.title, alias, self.commands[alias].fileplugin.title)
                else:
                    self.commands[alias] = command
            self.log_plugin_register(command)

        # register events
        for event_plugin in plugin.events:
            if event_plugin.is_catch_all():
                self.catch_all_events.append(event_plugin)
            else:
                for event_name in event_plugin.events:
                    if event_name in self.events:
                        self.events[event_name].append(event_plugin)
                    else:
                        self.events[event_name] = [event_plugin]
            self.log_plugin_register(event_plugin)

        # register regexes
        for regex_plugin in plugin.regexes:
            for regex_match in regex_plugin.regexes:
                self.regex_plugins.append((regex_match, regex_plugin))
            self.log_plugin_register(regex_plugin)

        # register sieves
        for sieve_plugin in plugin.sieves:
            self.sieves.append(sieve_plugin)
            self.log_plugin_register(sieve_plugin)

    def unregister_plugin(self, plugin, ignore_not_registered=False):
        """
        :param plugin: FilePlugin to directly unload, or str to lookup via filename and then unload.
        :type plugin: FilePlugin | str
        """
        if isinstance(plugin, str):
            if ignore_not_registered:
                if not plugin in self.plugins:
                    return
            else:
                assert plugin in self.plugins
            plugin = self.plugins[plugin]
        else:
            if ignore_not_registered:
                if not plugin.filename in self.plugins:
                    return
            else:
                assert plugin.filename in self.plugins
            assert self.plugins[plugin.filename] is plugin
            # we don't want to be unload a plugin which isn't loaded

        # unregister commands
        for command in plugin.commands:
            for alias in command.aliases:
                if alias in self.commands and self.commands[alias] == command:
                    # we need to make sure that there wasn't a conflict, and another plugin got this command.
                    del self.commands[alias]

        # unregister events
        for event_plugin in plugin.events:
            if event_plugin.is_catch_all():
                self.catch_all_events.remove(event_plugin)
            else:
                for event_name in event_plugin.events:
                    assert event_name in self.events  # this can't be not true
                    self.events[event_name].remove(event_plugin)

        # unregister regexes
        for regex_plugin in plugin.regexes:
            for regex_match in regex_plugin.regexes:
                self.regex_plugins.remove((regex_match, regex_plugin))

        # unregister sieves
        for sieve_plugin in plugin.sieves:
            self.sieves.remove(sieve_plugin)

        # remove last reference to plugin
        del self.plugins[plugin.filename]

        self.bot.logger.info("Unloaded all plugins from {}".format(plugin.title))

    def log_plugin_register(self, plugin):
        self.bot.logger.info(
            "Loading {} - {}".format(plugin.fileplugin.filename, plugin_desc(plugin)))


class FilePlugin:
    """
    :type filepath: str
    :type filename: str
    :type title: str
    :type code: object
    :type commands: list[CommandPlugin]
    :type regexes: list[RegexPlugin]
    :type events: list[EventPlugin]
    :type sieves: list[SievePlugin]
    """

    def __init__(self, filepath, filename, title, code):
        """
        :type filepath: str
        :type filename: str
        :type code: object
        """
        self.filepath = filepath
        self.filename = filename
        self.title = title
        self.code = code
        self.commands, self.regexes, self.events, self.sieves = find_hooks(self, code)


class Plugin:
    """
    :type type; str
    :type file_plugin: FilePlugin
    :type function: function
    :type function_name: str
    :type args: dict[str, unknown]
    """

    def __init__(self, plugin_type, file_plugin, func_hook):
        """
        :type plugin_type: str
        :type file_plugin: FilePlugin
        :type func_hook: hook._Hook
        """
        self.type = plugin_type
        self.fileplugin = file_plugin
        self.function = func_hook.function
        self.function_name = self.function.__name__
        self.args = func_hook.kwargs


class CommandPlugin(Plugin):
    """
    :type name: str
    :type aliases: list[str]
    :type doc: str
    :type autohelp: bool
    :type permissions: list[str]
    """

    def __init__(self, file_plugin, cmd_hook):
        """
        :type file_plugin: FilePlugin
        :type cmd_hook: hook._CommandHook
        """
        Plugin.__init__(self, "command", file_plugin, cmd_hook)

        # make sure that autohelp and permissions are set
        if not "autohelp" in cmd_hook.kwargs:
            self.autohelp = False
        if not "permissions" in cmd_hook.kwargs:
            self.permissions = []

        self.name = cmd_hook.main_alias
        self.aliases = list(cmd_hook.aliases)  # turn the set into a list
        self.aliases.remove(self.name)
        self.aliases.insert(0, self.name)  # make sure the name, or 'main alias' is in position 0
        self.doc = cmd_hook.doc


class RegexPlugin(Plugin):
    """
    :type regexes: set[re.__Regex]
    """

    def __init__(self, file_plugin, regex_hook):
        """
        :type file_plugin: FilePlugin
        :type regex_hook: hook._RegexHook
        """
        Plugin.__init__(self, "regex", file_plugin, regex_hook)
        self.regexes = regex_hook.regexes


class EventPlugin(Plugin):
    """
    :type events: set[str]
    """

    def __init__(self, file_plugin, event_hook):
        """
        :type file_plugin: FilePlugin
        :type event_hook: hook._EventHook
        """
        Plugin.__init__(self, "event", file_plugin, event_hook)
        self.events = event_hook.events

    def is_catch_all(self):
        return "*" in self.events


class SievePlugin(Plugin):
    def __init__(self, file_plugin, sieve_hook):
        """
        :type file_plugin: FilePlugin
        :type sieve_hook: hook._SieveHook
        """
        Plugin.__init__(self, "sieve", file_plugin, sieve_hook)


_hook_name_to_plugin = {
    "command": CommandPlugin,
    "regex": RegexPlugin,
    "event": EventPlugin,
    "sieve": SievePlugin,
}
