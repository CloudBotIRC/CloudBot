import asyncio
import enum
import glob
import importlib
import inspect
import logging
import os
import re
import itertools

from cloudbot.event import Event, HookEvent

logger = logging.getLogger("cloudbot")


class HookType(enum.Enum):
    on_start = 1,
    on_stop = 2,
    sieve = 3,
    event = 4,
    regex = 5,
    command = 6,
    irc_raw = 7,


def find_plugins(plugin_directories):
    """
    :type plugin_directories: collections.Iterable[str]
    :rtype: collections.Iterable[str]
    """
    for directory_pattern in plugin_directories:
        for directory in glob.iglob(directory_pattern):
            logger.info("Loading plugins from {}".format(directory))
            if not os.path.exists(os.path.join(directory, "__init__.py")):
                with open(os.path.join(directory, "__init__.py"), 'w') as file:
                    file.write('\n')  # create blank __init__.py file if none exists
            for plugin in glob.iglob(os.path.join(directory, '*.py')):
                yield plugin


def find_hooks(title, module):
    """
    :type title: str
    :type module: object
    :rtype: dict[HookType, list[Hook]
    """
    # set the loaded flag
    module._plugins_loaded = True
    hooks_dict = dict()
    for hook_type in HookType:
        hooks_dict[hook_type] = list()

    for name, func in module.__dict__.items():
        if hasattr(func, "bot_hooks"):
            # if it has cloudbot hook
            for hook in func.bot_hooks:
                hook_type = hook.type
                hook_class = _hook_classes[hook_type]
                hooks_dict[hook_type].append(hook_class(title, hook))

            # delete the hook to free memory
            del func.bot_hooks

    return hooks_dict


def _prepare_parameters(hook, base_event, hook_event):
    """
    Prepares arguments for the given hook

    :type hook: cloudbot.plugin.Hook
    :type base_event: cloudbot.event.Event
    :type hook_event: cloudbot.event.HookEvent
    :rtype: list
    """
    parameters = []
    for required_arg in hook.required_args:
        if hasattr(base_event, required_arg):
            value = getattr(base_event, required_arg)
            parameters.append(value)
        elif hasattr(hook_event, required_arg):
            value = getattr(hook_event, required_arg)
            parameters.append(value)
        else:
            logger.warning("Plugin {} asked for invalid argument '{}', cancelling execution!"
                           .format(hook.description, required_arg))
            logger.debug("Valid arguments are: {}".format(dir(base_event) + dir(hook_event)))
            return None
    return parameters


class PluginManager:
    """
    PluginManager is the core of CloudBot plugin loading.

    PluginManager loads Plugins, and adds their Hooks to easy-access dicts/lists.

    Each Plugin represents a file, and loads hooks onto itself using find_hooks.

    Plugins are the lowest level of abstraction in this class. There are four different plugin types:
    - CommandPlugin is for bot commands
    - RawPlugin hooks onto irc_raw irc lines
    - RegexPlugin loads a regex parameter, and executes on irc lines which match the regex
    - SievePlugin is a catch-all sieve, which all other plugins go through before being executed.

    :type bot: cloudbot.bot.CloudBot
    :type commands: dict[str, CommandHook]
    :type raw_triggers: dict[str, list[RawHook]]
    :type catch_all_triggers: list[RawHook]
    :type event_type_hooks: dict[cloudbot.event.EventType, list[EventHook]]
    :type regex_hooks: list[(re.__Regex, RegexHook)]
    :type sieves: list[SieveHook]
    """

    def __init__(self, bot):
        """
        Creates a new PluginManager. You generally only need to do this from inside cloudbot.bot.CloudBot
        :type bot: cloudbot.bot.CloudBot
        """
        self.bot = bot

        self.commands = {}
        self.raw_triggers = {}
        self.catch_all_triggers = []
        self.event_type_hooks = {}
        self.regex_hooks = []
        self.sieves = []
        self.shutdown_hooks = []
        self._hook_locks = {}

    @asyncio.coroutine
    def load_all(self, plugin_directories):
        """
        Load a plugin from each *.py file in the given directory.

        :type plugin_directories: collections.Iterable[str]
        """
        path_list = find_plugins(plugin_directories)
        # Load plugins asynchronously :O
        yield from asyncio.gather(*(self.load_plugin(path) for path in path_list), loop=self.bot.loop)

    @asyncio.coroutine
    def load_plugin(self, path):
        """
        Loads a plugin from the given path and plugin object, then registers all hooks from that plugin.

        :type path: str
        """
        file_path = os.path.abspath(path)
        relative_path = os.path.relpath(file_path, os.path.curdir)

        module_name = os.path.splitext(relative_path)[0].replace(os.path.sep, '.')
        if os.path.altsep:
            module_name = module_name.replace(os.path.altsep, '.')

        title = module_name
        if module_name.startswith('plugins.'):  # if it is in the default plugin dir, don't prepend plugins. to title
            title = title[len('plugins.'):]

        try:
            plugin_module = importlib.import_module(module_name)
        except Exception:
            logger.exception("Error loading {}:".format(file_path))
            return

        hooks = find_hooks(title, plugin_module)

        # proceed to register hooks

        # run on_start hooks
        on_start_event = Event(bot=self.bot)
        for on_start_hook in hooks[HookType.on_start]:
            success = yield from self.launch(on_start_hook, on_start_event)
            if not success:
                logger.warning("Not registering hooks from plugin {}: on_start hook errored".format(title))
                return

        # register events
        for event_hook in hooks[HookType.event]:
            for event_type in event_hook.types:
                if event_type in self.event_type_hooks:
                    self.event_type_hooks[event_type].append(event_hook)
                else:
                    self.event_type_hooks[event_type] = [event_hook]
            self._log_hook(event_hook)

        # register commands
        for command_hook in hooks[HookType.command]:
            for alias in command_hook.aliases:
                if alias in self.commands:
                    logger.warning(
                        "Plugin {} attempted to register command {} which was already registered by {}. "
                        "Ignoring new assignment.".format(title, alias, self.commands[alias].plugin))
                else:
                    self.commands[alias] = command_hook
            self._log_hook(command_hook)

        # register raw hooks
        for raw_hook in hooks[HookType.irc_raw]:
            if raw_hook.is_catch_all():
                self.catch_all_triggers.append(raw_hook)
            else:
                for trigger in raw_hook.triggers:
                    if trigger in self.raw_triggers:
                        self.raw_triggers[trigger].append(raw_hook)
                    else:
                        self.raw_triggers[trigger] = [raw_hook]
            self._log_hook(raw_hook)

        # register regex hooks
        for regex_hook in hooks[HookType.regex]:
            for regex in regex_hook.triggers:
                self.regex_hooks.append((regex, regex_hook))
            self._log_hook(regex_hook)

        # register sieves
        for sieve_hook in hooks[HookType.sieve]:
            self.sieves.append(sieve_hook)
            self._log_hook(sieve_hook)

        # register shutdown hooks
        for stop_hook in hooks[HookType.on_stop]:
            self.shutdown_hooks.append(stop_hook)
            self._log_hook(stop_hook)

    def _log_hook(self, hook):
        """
        Logs registering a given hook

        :type hook: Hook
        """
        if self.bot.config.get("logging", {}).get("show_plugin_loading", True):
            logger.debug("Loaded {}".format(repr(hook)))

    @asyncio.coroutine
    def _execute_hook(self, hook, base_event, hook_event):
        """
        Runs the specific hook with the given bot and event.

        Returns False if the hook errored, True otherwise.

        :type hook: cloudbot.plugin.Hook
        :type base_event: cloudbot.event.Event
        :type hook_event: cloudbot.event.HookEvent
        :rtype: bool
        """
        parameters = _prepare_parameters(hook, base_event, hook_event)
        if parameters is None:
            return False

        try:
            # _internal_run_threaded and _internal_run_coroutine prepare the database, and run the hook.
            # _internal_run_* will prepare parameters and the database session, but won't do any error catching.
            if hook.threaded:
                out = yield from self.bot.loop.run_in_executor(None, hook.function, *parameters)
            else:
                out = yield from hook.function(*parameters)
        except Exception:
            logger.exception("Error in hook {}".format(hook.description))
            base_event.message("Error in plugin '{}'.".format(hook.plugin))
            return False

        if out is not None:
            if isinstance(out, (list, tuple)):
                # if there are multiple items in the response, return them on multiple lines
                base_event.reply(*out)
            else:
                base_event.reply(*str(out).split('\n'))

        return True

    @asyncio.coroutine
    def _sieve(self, sieve, event, hook_event):
        """
        :type sieve: cloudbot.plugin.Hook
        :type event: cloudbot.event.Event
        :type hook_event: cloudbot.event.HookEvent
        :rtype: cloudbot.event.Event
        """
        try:
            if sieve.threaded:
                result = yield from self.bot.loop.run_in_executor(None, sieve.function, event, hook_event)
            else:
                result = yield from sieve.function(event, hook_event)
        except Exception:
            logger.exception("Error running sieve {} on {}:".format(sieve.description, hook_event.hook.description))
            return None
        else:
            return result

    @asyncio.coroutine
    def launch(self, hook, base_event, hevent=None):
        """
        Dispatch a given event to a given hook using a given bot object.

        Returns False if the hook didn't run successfully, and True if it ran successfully.

        :type base_event: cloudbot.event.Event
        :type hevent: cloudbot.event.HookEvent | cloudbot.event.CommandHookEvent
        :type hook: cloudbot.plugin.Hook | cloudbot.plugin.CommandHook
        :rtype: bool
        """

        if hevent is None:
            hevent = HookEvent(base_event=base_event, hook=hook)

        if hook.type not in (HookType.on_start, HookType.on_stop):  # we don't need sieves on on_start or on_stop hooks.
            for sieve in self.bot.plugin_manager.sieves:
                base_event = yield from self._sieve(sieve, base_event, hevent)
                if base_event is None:
                    return False

        if hook.type is HookType.command and hook.auto_help and not hevent.text and hook.doc is not None:
            hevent.notice_doc()
            return False

        if hook.single_thread:
            # There should only be once instance of this hook running at a time, so let's use a lock for it.
            key = (hook.plugin, hook.function_name)
            if key not in self._hook_locks:
                self._hook_locks[key] = asyncio.Lock(loop=self.bot.loop)

            # Run the plugin with the message, and wait for it to finish
            with (yield from self._hook_locks[key]):
                result = yield from self._execute_hook(hook, base_event, hevent)
        else:
            # Run the plugin with the message, and wait for it to finish
            result = yield from self._execute_hook(hook, base_event, hevent)

        # Return the result
        return result

    @asyncio.coroutine
    def run_shutdown_hooks(self):
        shutdown_event = Event(bot=self.bot)
        tasks = (self.launch(hook, shutdown_event) for hook in self.shutdown_hooks)
        yield from asyncio.gather(*tasks, loop=self.bot.loop)


class Hook:
    """
    Each hook is specific to one function. This class is never used by itself, rather extended.

    :type type: HookType
    :type plugin: str
    :type function: callable
    :type function_name: str
    :type required_args: list[str]
    :type threaded: bool
    :type run_first: bool
    :type permissions: list[str]
    :type single_thread: bool
    """
    type = None  # to be assigned in subclasses

    def __init__(self, plugin, hook_decorator):
        """
        :type plugin: str
        """
        self.plugin = plugin
        self.function = hook_decorator.function
        self.function_name = self.function.__name__

        self.required_args = inspect.getargspec(self.function)[0]
        if self.required_args is None:
            self.required_args = []

        if asyncio.iscoroutine(self.function) or asyncio.iscoroutinefunction(self.function):
            self.threaded = False
        else:
            self.threaded = True

        self.permissions = hook_decorator.kwargs.pop("permissions", [])
        self.single_thread = hook_decorator.kwargs.pop("single_instance", False)
        self.run_first = hook_decorator.kwargs.pop("run_first", False)

        if hook_decorator.kwargs:
            # we should have popped all the args, so warn if there are any left
            logger.warning("Ignoring extra args {} from {}".format(hook_decorator.kwargs, self.description))

    @property
    def description(self):
        return "{}:{}".format(self.plugin, self.function_name)

    def __repr__(self, **kwargs):
        result = "type: {}, plugin: {}, permissions: {}, run_first: {}, single_instance: {}, threaded: {}".format(
            self.type.name, self.plugin, self.permissions, self.run_first, self.single_thread, self.threaded)
        if kwargs:
            result = ", ".join(itertools.chain(("{}: {}".format(*item) for item in kwargs.items()), (result,)))

        return "{}[{}]".format(type(self).__name__, result)


class OnStartHook(Hook):
    type = HookType.on_start


class OnStopHook(Hook):
    type = HookType.on_stop


class SieveHook(Hook):
    type = HookType.sieve


class EventHook(Hook):
    """
    :type types: set[cloudbot.event.EventType]
    """
    type = HookType.event

    def __init__(self, plugin, decorator):
        """
        :type plugin: Plugin
        :type decorator: cloudbot.hook.EventDecorator
        """
        self.types = decorator.triggers

        super().__init__(plugin, decorator)


class RegexHook(Hook):
    """
    :type triggers: set[re.__Regex]
    """
    type = HookType.regex

    def __init__(self, plugin, decorator):
        """
        :type plugin: Plugin
        :type decorator: cloudbot.hook.RegexDecorator
        """
        self.triggers = decorator.triggers

        super().__init__(plugin, decorator)

    def __repr__(self):
        return super().__repr__(triggers=", ".join(regex.pattern for regex in self.triggers))


class CommandHook(Hook):
    """
    :type name: str
    :type aliases: list[str]
    :type doc: str
    :type auto_help: bool
    """
    type = HookType.command

    def __init__(self, plugin, decorator):
        """
        :type plugin: str
        :type decorator: cloudbot.hook.CommandDecorator
        """
        self.auto_help = decorator.kwargs.pop("autohelp", True)

        self.name = decorator.main_alias
        self.aliases = list(decorator.triggers)  # turn the set into a list
        self.aliases.remove(self.name)
        self.aliases.insert(0, self.name)  # make sure the name, or 'main alias' is in position 0
        self.doc = decorator.doc

        super().__init__(plugin, decorator)

    def __repr__(self):
        return super().__repr__(name=self.name, aliases=self.aliases[1:])


class RawHook(Hook):
    """
    :type triggers: set[str]
    """
    type = HookType.irc_raw

    def __init__(self, plugin, decorator):
        """
        :type plugin: Plugin
        :type decorator: cloudbot.hook.IrcRawDecorator
        """
        self.triggers = decorator.triggers

        super().__init__(plugin, decorator)

    def is_catch_all(self):
        return "*" in self.triggers

    def __repr__(self):
        return super().__repr__(triggers=self.triggers)


_hook_classes = {
    HookType.on_start: OnStartHook,
    HookType.on_stop: OnStopHook,
    HookType.sieve: SieveHook,
    HookType.event: EventHook,
    HookType.regex: RegexHook,
    HookType.command: CommandHook,
    HookType.irc_raw: RawHook,
}
