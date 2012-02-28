import inspect
import re


def _hook_add(func, add, name=''):
    if not hasattr(func, '_hook'):
        func._hook = []
    func._hook.append(add)

    if not hasattr(func, '_filename'):
        func._filename = func.func_code.co_filename

    if not hasattr(func, '_args'):
        argspec = inspect.getargspec(func)
        if name:
            n_args = len(argspec.args)
            if argspec.defaults:
                n_args -= len(argspec.defaults)
            if argspec.keywords:
                n_args -= 1
            if argspec.varargs:
                n_args -= 1
            if n_args != 1:
                err = '%ss must take 1 non-keyword argument (%s)' % (name,
                            func.__name__)
                raise ValueError(err)

        args = []
        if argspec.defaults:
            end = bool(argspec.keywords) + bool(argspec.varargs)
            args.extend(argspec.args[-len(argspec.defaults):
                        end if end else None])
        if argspec.keywords:
            args.append(0)  # means kwargs present
        func._args = args

    if not hasattr(func, '_thread'):  # does function run in its own thread?
        func._thread = False


def sieve(func):
    if func.func_code.co_argcount != 5:
        raise ValueError(
                'sieves must take 5 arguments: (bot, input, func, type, args)')
    _hook_add(func, ['sieve', (func,)])
    return func


def command(arg=None, **kwargs):
    args = {}

    def command_wrapper(func):
        args.setdefault('name', func.func_name)
        _hook_add(func, ['command', (func, args)], 'command')
        return func

    if kwargs or not inspect.isfunction(arg):
        if arg is not None:
            args['name'] = arg
        args.update(kwargs)
        return command_wrapper
    else:
        return command_wrapper(arg)


def event(arg=None, **kwargs):
    args = kwargs

    def event_wrapper(func):
        args['name'] = func.func_name
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
        args['name'] = func.func_name
        args['regex'] = regex
        args['re'] = re.compile(regex, flags)
        _hook_add(func, ['regex', (func, args)], 'regex')
        return func

    if inspect.isfunction(regex):
        raise ValueError("regex decorators require a regex to match against")
    else:
        return regex_wrapper
