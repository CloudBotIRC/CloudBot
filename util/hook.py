import inspect
import re


def _hook_add(func, add, name=''):
    if not hasattr(func, '_hook'):
        func._hook = []
    func._hook.append(add)

    if not hasattr(func, '_filename'):
        func._filename = func.__code__.co_filename

    if not hasattr(func, '_thread'):  # does function run in its own thread?
        func._thread = False


def sieve(func):
    if func.__code__.co_argcount != 5:
        raise ValueError(
            'sieves must take 5 arguments: (bot, input, func, type, args)')
    _hook_add(func, ['sieve', (func,)])
    return func

# TODO: Add support for multiple commands in one hook
# EG: @hook.command(["command1", "command2"], **args)
def command(name=None, **kwargs):
    args = {}

    def command_wrapper(func):
        args.setdefault('name', func.__name__)
        _hook_add(func, ['command', (func, args)], 'command')
        return func

    if kwargs or not inspect.isfunction(name):
        if name is not None:
            args['name'] = name
        args.update(kwargs)
        return command_wrapper
    else:
        return command_wrapper(name)


def event(arg=None, **kwargs):
    args = kwargs

    def event_wrapper(func):
        args['name'] = func.__name__
        args.setdefault('events', ['*'])
        _hook_add(func, ['event', (func, args)], 'event')
        return func

    if inspect.isfunction(arg):
        return event_wrapper(arg, kwargs)
    else:
        if arg is not None:
            args['events'] = arg.split()
        return event_wrapper


def singlethread(func):
    func._thread = True
    return func


def regex(regex, flags=0, **kwargs):
    args = kwargs

    def regex_wrapper(func):
        args['name'] = func.__name__
        args['regex'] = regex
        args['re'] = re.compile(regex, flags)
        _hook_add(func, ['regex', (func, args)], 'regex')
        return func

    if inspect.isfunction(regex):
        raise ValueError("regex decorators require a regex to match against")
    else:
        return regex_wrapper
