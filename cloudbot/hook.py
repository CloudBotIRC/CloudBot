import re

from cloudbot.event import EventType
from cloudbot.plugin import HookType

valid_command_re = re.compile(r"^[\w_-]+$")


class _DecoratorClass():
    """
    :type function: callable
    """

    def __init__(self):
        self.function = None

    def __call__(self, function):
        if self.function is not None:
            raise ValueError("Already hooked to a function")
        if not callable(function):
            raise ValueError("Function must be callable")

        self.function = function
        if function.__doc__:
            self.doc = function.__doc__.split('\n', 1)[0]
        else:
            self.doc = None

        if hasattr(function, "bot_hooks"):
            function.bot_hooks.append(self)
        else:
            # noinspection PyUnresolvedReferences
            function.bot_hooks = [self]

        return function


class OnStartDecorator(_DecoratorClass):
    """
    :type kwargs: dict[str, V]
    """
    type = HookType.on_start

    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs


class OnStopDecorator(_DecoratorClass):
    """
    :type kwargs: dict[str, V]
    """
    type = HookType.on_stop

    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs


class SieveDecorator(_DecoratorClass):
    """
    :type kwargs: dict[str, V]
    """
    type = HookType.sieve

    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs


class EventDecorator(_DecoratorClass):
    """
    :type kwargs: dict[str, V]
    :type triggers: tuple[EventType]
    """
    type = HookType.event

    def __init__(self, *triggers, **kwargs):
        super().__init__()
        if not triggers:
            raise ValueError("Must provide at least one trigger")

        for trigger in triggers:
            if not isinstance(trigger, EventType):
                raise ValueError("Invalid event trigger '{}'".format(trigger))

        self.triggers = triggers
        self.kwargs = kwargs


class RegexDecorator(_DecoratorClass):
    """
    :type kwargs: dict[str, V]
    :type triggers: tuple[re.__Regex]
    """
    type = HookType.regex

    def __init__(self, *triggers, **kwargs):
        """
        :type triggers: tuple[str | re.__Regex]
        """
        super().__init__()
        if not triggers:
            raise ValueError("Must provide at least one trigger")

        # Compile all string regex triggers
        triggers = (re.compile(text) for text in triggers if isinstance(text, str))

        # Ensure all triggers are valid
        for regex_trigger in triggers:
            if not hasattr(regex_trigger, "search"):
                raise ValueError("Invalid regex trigger '{}'".format(regex_trigger))

        self.triggers = triggers
        self.kwargs = kwargs


class CommandDecorator(_DecoratorClass):
    """
    :type kwargs: dict[str, V]
    :type triggers: tuple[str]
    """
    type = HookType.command

    def __init__(self, *triggers, **kwargs):
        super().__init__()

        for trigger in triggers:
            if not valid_command_re.match(trigger):
                raise ValueError("Invalid command trigger '{}'".format(trigger))

        self.kwargs = kwargs
        if triggers:
            self.triggers = triggers
            self.main_alias = triggers[0]
        else:
            self.triggers = None
            self.main_alias = None

    def __call__(self, function):
        super().__call__(function)

        if self.triggers is None:
            trigger = function.__name__
            self.triggers = (trigger,)
            self.main_alias = trigger

        if function.__doc__:
            self.doc = function.__doc__.split('\n', 1)[0]
        else:
            self.doc = None


class IrcRawDecorator(_DecoratorClass):
    """
    :type kwargs: dict[str, V]
    :type triggers: tuple[str]
    """
    type = HookType.irc_raw

    def __init__(self, *triggers, **kwargs):
        super().__init__()
        if not triggers:
            raise ValueError("Must provide at least one trigger")

        self.triggers = triggers
        self.kwargs = kwargs


on_start = OnStartDecorator
on_stop = OnStopDecorator
sieve = SieveDecorator
event = EventDecorator
regex = RegexDecorator
command = CommandDecorator
irc_raw = IrcRawDecorator
