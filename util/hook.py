import inspect
import re


class IllegalCommandException(Exception):
    pass


class _Hook():
    """
    :type function: function
    :type type: str
    :type kwargs: dict[str, unknown]
    """

    def __init__(self, function, hook_type, kwargs):
        """
        :type function: function
        :type hook_type: str
        :type kwargs: dict[str, unknown]
        """
        self.function = function
        self.type = hook_type
        self.kwargs = kwargs


class _CommandHook(_Hook):
    """
    :type main_alias: str
    :type aliases: set[str]
    """

    def __init__(self, alias_param, function, kwargs):
        """
        :type alias_param: list[str] | str
        :type function: function
        :type kwargs: dict[str, V]
        """
        _Hook.__init__(self, function, "command", kwargs)

        if isinstance(alias_param, str):
            self.main_alias = alias_param
            if not re.match(r'^\w+$', alias_param):
                raise IllegalCommandException("Invalid command name {}".format(alias_param))
            self.aliases = {alias_param}  # construct a set with one str
        else:
            assert isinstance(alias_param, list)
            self.main_alias = alias_param[0]
            for alias in alias_param:
                if not re.match(r'^\w+$', alias):
                    raise IllegalCommandException("Invalid command name {}".format(alias))
            self.aliases = set(alias_param)  # turn the list into a set

        if function.__doc__:
            self.doc = function.__doc__.split('\n', 1)[0]
        else:
            self.doc = None

    def add_hook(self, alias_param, kwargs):
        """
        :type alias_param: list[str] | str
        """
        # update kwargs, overwriting duplicates
        self.kwargs.update(kwargs)

        if isinstance(alias_param, str):
            if not re.match(r'^\w+$', alias_param):
                raise IllegalCommandException("Invalid command name {}".format(alias_param))
            self.aliases.add(alias_param)
        else:
            assert isinstance(alias_param, list)
            for alias in alias_param:
                if not re.match(r'^\w+$', alias):
                    raise IllegalCommandException("Invalid command name {}".format(alias))
            self.aliases.update(alias_param)


class _RegexHook(_Hook):
    """
    :type regexes: list[re.__Regex]
    """

    def __init__(self, function, regex_param, regex_flags, kwargs):
        """
        :type function: function
        :type regex_param: str | re.__Regex | list[str | re.__Regex]
        :type kwargs: dict[str, V]
        """
        _Hook.__init__(self, function, "regex", kwargs)

        self.regexes = []
        if isinstance(regex_param, str):
            # if the paramater is a string, compile and add
            self.regexes.append(re.compile(regex_param, regex_flags))
        elif hasattr(regex_param, "search"):
            # if the paramater is an re.__Regex, just add it
            # we only use regex.search anyways, so this is a good determiner
            self.regexes.append(regex_param)
        else:
            assert isinstance(regex_param, list)
            # if the paramater is a list, add each one
            for re_to_match in regex_param:
                if isinstance(re_to_match, str):
                    re_to_match = re.compile(re_to_match, regex_flags)
                else:
                    # make sure that the param is a regex if it isn't a str
                    assert isinstance(re_to_match, re.__Regex)

                self.regexes.append(re_to_match)

    def add_hook(self, regex_param, regex_flags, kwargs):
        """
        :type regex_param: list[str | re.__Regex] | str | re.__Regex
        :type kwargs: dict[str, V]
        """
        # update kwargs, overwriting duplicates
        self.kwargs.update(kwargs)
        # add all regex_paramaters to valid regexes
        if isinstance(regex_param, str):
            # if the paramater is a string, compile and add
            self.regexes.append(re.compile(regex_param, regex_flags))
        elif hasattr(regex_param, "search"):
            # if the paramater is an re.__Regex, just add it
            # we only use regex.search anyways, so this is a good determiner
            self.regexes.append(regex_param)
        else:
            assert isinstance(regex_param, list)
            # if the paramater is a list, add each one
            for re_to_match in regex_param:
                if isinstance(re_to_match, str):
                    re_to_match = re.compile(re_to_match, regex_flags)
                else:
                    assert isinstance(re_to_match, re.__Regex)

                self.regexes.append(re_to_match)


class _EventHook(_Hook):
    """
    :type events: set[str]
    """

    def __init__(self, event_param, function, kwargs):
        """
        :type event_param: list[str] | str
        :type function: function
        :type kwargs: dict[str, V]
        """
        _Hook.__init__(self, function, "event", kwargs)

        if isinstance(event_param, str):
            self.events = {event_param}  # one str set
        else:
            assert isinstance(event_param, list)
            self.events = set(event_param)

    def add_hook(self, event_param, kwargs):
        """
        :type event_param: list[str] | str
        :type kwargs: dict[str, V]
        """
        # update kwargs, overwriting duplicates
        self.kwargs.update(kwargs)

        if isinstance(event_param, str):
            self.events.add(event_param)
        else:
            assert isinstance(event_param, list)
            self.events.update(event_param)


class _SieveHook(_Hook):
    def __init__(self, function, kwargs):
        _Hook.__init__(self, function, "sieve", kwargs)
        # there isn't that much else to do, as sieves don't have any params

    def add_hook(self, kwargs):
        # update kwargs, overwriting duplicates
        self.kwargs.update(kwargs)


class _OnLoadHook(_Hook):
    def __init__(self, function, kwargs):
        _Hook.__init__(self, function, "onload", kwargs)
        # there isn't that much else to do, as onload plugins don't have params

    def add_hook(self, kwargs):
        # update kwargs, overwriting duplicates
        self.kwargs.update(kwargs)


def _add_hook(func, hook):
    if not hasattr(func, "_cloudbot_hook"):
        func._cloudbot_hook = {}
        # print("creating cloudbot hook on {}: {}".format(func.__name__, func.__dict__))
    else:
        assert hook.type not in func._cloudbot_hook  # in this case the hook should be using the add_hook method
    func._cloudbot_hook[hook.type] = hook


def _get_hook(func, hook_type):
    if hasattr(func, "_cloudbot_hook") and hook_type in func._cloudbot_hook:
        return func._cloudbot_hook[hook_type]

    return None


def _command_hook(func, alias_param=None, **kwargs):
    """this is the internal command decorator
    :type func: function
    :type alias_param: list[str] | str
    """
    if not alias_param:
        alias_param = func.__name__

    command_hook = _get_hook(func, "command")
    if command_hook:
        assert isinstance(command_hook, _CommandHook)
        command_hook.add_hook(alias_param, kwargs)
    else:
        _add_hook(func, _CommandHook(alias_param, func, kwargs))

    return func


def _event_hook(func, event_param, **kwargs):
    """this is the interal event hook
    :type func: function
    :type event_param: list[str] | str
    """

    event_hook = _get_hook(func, "event")
    if event_hook:
        assert isinstance(event_hook, _EventHook)
        event_hook.add_hook(event_param, kwargs)
    else:
        _add_hook(func, _EventHook(event_param, func, kwargs))

    return func


def _regex_hook(func, regex_param, flags, **kwargs):
    """this is the internal regex hook
    :type regex_param: str | re.__Regex | list[str | re.__Regex]
    :type flags: int
    """

    regex_hook = _get_hook(func, "regex")
    if regex_hook:
        assert isinstance(regex_hook, _RegexHook)
        regex_hook.add_hook(regex_param, flags, kwargs)
    else:
        _add_hook(func, _RegexHook(func, regex_param, flags, kwargs))

    return func


def _sieve_hook(func, **kwargs):
    assert len(inspect.getargspec(func).args) == 3, \
        "Sieve plugin has incorrect argument count. Needs params: bot, input, plugin"

    sieve_hook = _get_hook(func, "sieve")
    if sieve_hook:
        assert isinstance(sieve_hook, _SieveHook)
        sieve_hook.add_hook(kwargs)
    else:
        _add_hook(func, _SieveHook(func, kwargs))

    return func


def _onload_hook(func, **kwargs):
    on_load_hook = _get_hook(func, "onload")
    if on_load_hook:
        assert isinstance(on_load_hook, _OnLoadHook)
        on_load_hook.add_hook(kwargs)
    else:
        _add_hook(func, _OnLoadHook(func, kwargs))

    return func


def command(param=None, **kwargs):
    """External command decorator. Can be used directly as a decorator, or with args to return a decorator.
    :type param: str | list[str] | function
    """
    if callable(param):  # this decorator is being used directly
        return _command_hook(param)
    else:  # this decorator is being used indirectly, so return a decorator function
        return lambda func: _command_hook(func, alias_param=param, **kwargs)


def event(event_param, **kwargs):
    """External event decorator. Must be used as a function to return a decorator
    :type event_param: str | list[str]
    """
    if callable(event_param):  # this decorator is being used directly, which isn't good
        raise TypeError("The event hook must be used as a function that returns a decorator")
    else:  # this decorator is being used as a function, so return a decorator
        return lambda func: _event_hook(func, event_param, **kwargs)


def regex(regex_param, flags=0, **kwargs):
    """External regex decorator. Must be used as a function to return a decorator.
    :type regex_param: str | re.__Regex | list[str | re.__Regex]
    :type flags: int
    """
    if callable(regex_param):  # this decorator is being used directly, which isn't good
        raise TypeError("The regex hook must be used as a function that returns a decorator")
    else:  # this decorator is being used as a function, so return a decorator
        return lambda func: _regex_hook(func, regex_param, flags, **kwargs)


def sieve(param=None, **kwargs):
    """External sieve decorator. Can be used directly as a decorator, or with args to return a decorator
    :type param: function | None
    """
    if callable(param):
        return _sieve_hook(param, **kwargs)
    else:
        return lambda func: _sieve_hook(func, **kwargs)


def onload(param=None, **kwargs):
    """External onload decorator. Can be used directly as a decorator, or with args to return a decorator
    :type param: function | None
    """
    if callable(param):
        return _onload_hook(param, **kwargs)
    else:
        return lambda func: _onload_hook(func, **kwargs)