import re

from cloudbot.event import EventType
from cloudbot.plugin import HookType

valid_command_re = re.compile(r"^[\w_-]+$")


class _DecoratorClass():
    """
    :type function: callable
    """
    # to be assigned in sub-classes
    type = None

    def __init__(self, function=None):
        self.function = None

        # legacy - support calling directly with function
        if function is not None and callable(function):
            self.__call__(function)

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

        if hasattr(function, "cloudbot_hooks"):
            function.cloudbot_hooks.append(self)
        else:
            # noinspection PyUnresolvedReferences
            function.cloudbot_hooks = [self]

        return function


class OnStartDecorator(_DecoratorClass):
    """
    :type kwargs: dict[str, V]
    """
    type = HookType.on_start

    def __init__(self, function=None, **kwargs):
        super().__init__(function=function)  # legacy - support calling directly with function
        self.kwargs = kwargs


class OnStopDecorator(_DecoratorClass):
    """
    :type kwargs: dict[str, V]
    """
    type = HookType.on_stop

    def __init__(self, function=None, **kwargs):
        super().__init__(function=function)  # legacy - support calling directly with function
        self.kwargs = kwargs


class PeriodicDecorator(_DecoratorClass):
    """
    :type kwargs: dict[str, V]
    :type interval: int | float
    :type initial_interval: int | float
    """
    type = HookType.periodic

    def __init__(self, interval=None, **kwargs):
        super().__init__()
        self.kwargs = kwargs

        if interval is None:
            self.interval = 60.0
        elif callable(interval):
            # legacy - support calling directly with function
            self.__call__(interval)
        else:
            self.interval = interval


class SieveDecorator(_DecoratorClass):
    """
    :type kwargs: dict[str, V]
    """
    type = HookType.sieve

    def __init__(self, function=None, **kwargs):
        super().__init__(function=function)  # legacy - support calling directly with function
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

        # legacy - support @hook.event([trigger1, trigger2]) syntax
        if len(triggers) == 1 and (isinstance(triggers[0], list) or isinstance(triggers[0], tuple)):
            triggers = triggers[0]

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

        # legacy - support @hook.regex([trigger1, trigger2]) syntax
        if len(triggers) == 1 and (isinstance(triggers[0], list) or isinstance(triggers[0], tuple)):
            triggers = triggers[0]

        # Compile all string regex triggers
        compiled_triggers = []
        for trigger in triggers:
            if isinstance(trigger, str):
                trigger = re.compile(trigger)
            if not hasattr(trigger, "search"):
                raise ValueError("Invalid regex trigger '{}'".format(trigger))
            compiled_triggers.append(trigger)

        self.triggers = tuple(compiled_triggers)
        self.kwargs = kwargs


class CommandDecorator(_DecoratorClass):
    """
    :type kwargs: dict[str, V]
    :type triggers: tuple[str]
    """
    type = HookType.command

    def __init__(self, *triggers, **kwargs):
        super().__init__()

        # legacy - support calling directly with function
        if len(triggers) == 1 and callable(triggers[0]):
            self.triggers = None
            self.main_alias = None
            self.__call__(triggers[0])
            return

        # legacy - support @hook.command([trigger1, trigger2]) syntax
        if len(triggers) == 1 and (isinstance(triggers[0], list) or isinstance(triggers[0], tuple)):
            triggers = triggers[0]

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
        result = super().__call__(function)

        if self.triggers is None:
            trigger = function.__name__
            self.triggers = (trigger,)
            self.main_alias = trigger

        if function.__doc__:
            self.doc = function.__doc__.split('\n', 1)[0]
        else:
            self.doc = None

        return result  # Return the result of super().__call__(function)


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

        # legacy - support @hook.irc_raw([trigger1, trigger2]) syntax
        if len(triggers) == 1 and (isinstance(triggers[0], list) or isinstance(triggers[0], tuple)):
            triggers = triggers[0]

        self.triggers = triggers
        self.kwargs = kwargs


on_start = OnStartDecorator
on_stop = OnStopDecorator
periodic = PeriodicDecorator
sieve = SieveDecorator
event = EventDecorator
regex = RegexDecorator
command = CommandDecorator
irc_raw = IrcRawDecorator
onload = on_start  # legacy - support @hook.onload()
