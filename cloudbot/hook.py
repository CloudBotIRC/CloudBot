import inspect
import re
import collections

from cloudbot.event import EventType
from cloudbot.plugin import HookType

valid_command_re = re.compile(r"^[\w-]+$")


class _Hook():
    """
    :type function: function
    :type type: HookType
    :type kwargs: dict[str, unknown]
    """
    type = None  # subclasses should define this

    def __init__(self, function):
        """
        :type function: function
        """
        self.function = function
        self.kwargs = {}

    def _add_hook(self, **kwargs):
        """
        :type kwargs: dict[str, unknown]
        """
        # update kwargs, overwriting duplicates
        self.kwargs.update(kwargs)


class _CommandHook(_Hook):
    """
    :type main_alias: str
    :type aliases: set[str]
    """
    type = HookType.command

    def __init__(self, function):
        """
        :type function: function
        """
        _Hook.__init__(self, function)
        self.aliases = set()
        self.main_alias = None

        if function.__doc__:
            self.doc = function.__doc__.split('\n', 1)[0]
        else:
            self.doc = None

    def add_hook(self, *aliases, **kwargs):
        """
        :type aliases: list[str] | str
        """
        self._add_hook(**kwargs)

        if not aliases:
            aliases = [self.function.__name__]
        elif len(aliases) == 1 and not isinstance(aliases[0], str):
            # we are being passed a list as the first argument, so aliases is in the form of ([item1, item2])
            aliases = aliases[0]

        if not self.main_alias:
            self.main_alias = aliases[0]

        for alias in aliases:
            if not valid_command_re.match(alias):
                raise ValueError("Invalid command name {}".format(alias))
        self.aliases.update(aliases)


class _RegexHook(_Hook):
    """
    :type regexes: list[re.__Regex]
    """
    type = HookType.regex

    def __init__(self, function):
        """
        :type function: function
        """
        _Hook.__init__(self, function)
        self.regexes = []

    def add_hook(self, *regexes, **kwargs):
        """
        :type regexes: Iterable[str | re.__Regex] | str | re.__Regex
        :type kwargs: dict[str, unknown]
        """
        self._add_hook(**kwargs)

        # If we have one argument, and that argument is neither a string or a compiled regex, we're being passed a list
        if len(regexes) == 1 and not (isinstance(regexes[0], str) or hasattr(regexes[0], "search")):
            regexes = regexes[0]  # it's a list we're being passed as the first argument, so take it as a list

        assert isinstance(regexes, collections.Iterable)
        # if the parameter is a list, add each one
        for re_to_match in regexes:
            if isinstance(re_to_match, str):
                re_to_match = re.compile(re_to_match)
            # make sure that the param is either a compiled regex, or has a search attribute.
            assert hasattr(re_to_match, "search")
            self.regexes.append(re_to_match)


class _RawHook(_Hook):
    """
    :type triggers: set[str]
    """
    type = HookType.irc_raw

    def __init__(self, function):
        """
        :type function: function
        """
        _Hook.__init__(self, function)
        self.triggers = set()

    def add_hook(self, *triggers, **kwargs):
        """
        :type triggers: list[str] | str
        :type kwargs: dict[str, unknown]
        """
        self._add_hook(**kwargs)
        if len(triggers) == 1 and not isinstance(triggers[0], str):
            # we are being passed a list as the first argument, so triggers is in the form of ([item1, item2])
            triggers = triggers[0]

        self.triggers.update(triggers)


class _EventHook(_Hook):
    """
    :type types: set[cloudbot.event.EventType]
    """
    type = HookType.event

    def __init__(self, function):
        """
        :type function: function
        """
        _Hook.__init__(self, function)
        self.types = set()

    def add_hook(self, *events, **kwargs):
        """
        :type events: tuple[cloudbot.event.EventType] | (list[cloudbot.event.EventType])
        :type kwargs: dict[str, unknown]
        """
        self._add_hook(**kwargs)

        if len(events) == 1 and not isinstance(events[0], EventType):
            # we are being passed a list as the first argument, so events is in the form of ([item1, item2])
            events = events[0]

        self.types.update(events)


class _SieveHook(_Hook):
    type = HookType.sieve

    def add_hook(self, **kwargs):
        self._add_hook(**kwargs)


class _OnStartHook(_Hook):
    type = HookType.on_start

    def add_hook(self, **kwargs):
        self._add_hook(**kwargs)


class _OnStopHook(_Hook):
    type = HookType.on_stop

    def add_hook(self, **kwargs):
        self._add_hook(**kwargs)


_hook_name_to_hook = {
    HookType.command: _CommandHook,
    HookType.regex: _RegexHook,
    HookType.irc_raw: _RawHook,
    HookType.event: _EventHook,
    HookType.sieve: _SieveHook,
    HookType.on_start: _OnStartHook,
    HookType.on_stop: _OnStopHook,
}


def _get_or_add_hook(func, hook_type):
    if hasattr(func, "plugin_hook"):
        if hook_type in func.plugin_hook:
            hook = func.plugin_hook[hook_type]
        else:
            hook = _hook_name_to_hook[hook_type](func)  # Make a new hook
            func.plugin_hook[hook_type] = hook
    else:
        hook = _hook_name_to_hook[hook_type](func)  # Make a new hook
        func.plugin_hook = {hook_type: hook}

    return hook


def command(*aliases, **kwargs):
    """External command decorator. Can be used directly as a decorator, or with args to return a decorator.
    :type param: tuple[str] | (list[str]) | (function)
    """

    def decorator(func):
        hook = _get_or_add_hook(func, HookType.command)

        if len(aliases) == 1 and callable(aliases[0]):
            hook.add_hook(**kwargs)  # we don't want to pass the function as an argument
        else:
            hook.add_hook(*aliases, **kwargs)

        return func

    if len(aliases) == 1 and callable(aliases[0]):  # this decorator is being used directly
        return decorator(aliases[0])
    else:  # this decorator is being used indirectly, so return a decorator function
        return decorator


def irc_raw(*triggers, **kwargs):
    """External raw decorator. Must be used as a function to return a decorator
    :type triggers: tuple[str] | (list[str])
    """

    def decorator(func):
        hook = _get_or_add_hook(func, HookType.irc_raw)
        hook.add_hook(*triggers, **kwargs)
        return func

    if len(triggers) == 1 and callable(triggers[0]):  # this decorator is being used directly, which isn't good
        raise TypeError("irc_raw() must be used as a function that returns a decorator")
    else:  # this decorator is being used as a function, so return a decorator
        return decorator


def event(*triggers, **kwargs):
    """External event decorator. Must be used as a function to return a decorator
    :type triggers: tuple[cloudbot.event.EventType] | (list[cloudbot.event.EventType])
    """

    def decorator(func):
        hook = _get_or_add_hook(func, HookType.event)
        hook.add_hook(*triggers, **kwargs)
        return func

    if len(triggers) == 1 and callable(triggers[0]):  # this decorator is being used directly, which isn't good
        raise TypeError("event() must be used as a function that returns a decorator")
    else:  # this decorator is being used as a function, so return a decorator
        return decorator


def regex(*regexes, **kwargs):
    """External regex decorator. Must be used as a function to return a decorator.
    :type regexes: tuple[str | re.__Regex] | (list[str | re.__Regex])
    :type flags: int
    """

    def decorator(func):
        hook = _get_or_add_hook(func, HookType.regex)
        hook.add_hook(*regexes, **kwargs)
        return func

    if len(regexes) == 1 and callable(regexes[0]):  # this decorator is being used directly, which isn't good
        raise TypeError("regex() hook must be used as a function that returns a decorator")
    else:  # this decorator is being used as a function, so return a decorator
        return decorator


def sieve(param=None, **kwargs):
    """External sieve decorator. Can be used directly as a decorator, or with args to return a decorator
    :type param: function | None
    """

    def decorator(func):
        if len(inspect.getargspec(func).args) != 1:
            raise ValueError(
                "Sieve plugin has too many or too few arguments. Sieves should only accept one argument: 'event'")

        hook = _get_or_add_hook(func, HookType.sieve)
        hook.add_hook(**kwargs)

        return func

    if callable(param):
        return decorator(param)
    else:
        return decorator


def on_start(param=None, **kwargs):
    """External on start decorator. Can be used directly as a decorator, or with args to return a decorator
    :type param: function | None
    """

    def decorator(func):
        hook = _get_or_add_hook(func, HookType.on_start)
        hook.add_hook(**kwargs)
        return func

    if callable(param):
        return decorator(param)
    else:
        return decorator


def on_stop(param=None, **kwargs):
    """External on stop decorator. Can be used directly as a decorator, or with args to return a decorator
    :type param: function | None
    """

    def decorator(func):
        hook = _get_or_add_hook(func, HookType.on_stop)
        hook.add_hook(**kwargs)
        return func

    if callable(param):
        return decorator(param)
    else:
        return decorator
