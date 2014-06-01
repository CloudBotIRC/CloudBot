from cloudbot import hook, web


@hook.command
def shorten(text):
    """shorten <url> [custom] - Shorten a url."""
    args = text.split()
    url = args[0]

    try:
        return web.shorten(url)
    except web.ServiceError as e:
        return e.message


@hook.command
def isgd(text):
    """isgd <url> [custom] - Shorten a url with is.gd. [custom] is an optional custom shortlink."""
    args = text.split()
    url = args[0]
    custom = args[1] if len(args) > 1 else None

    try:
        return web.shorten(url, custom, 'is.gd')
    except web.ServiceError as e:
        return e.message


@hook.command
def gitio(text):
    """gitio <url> [custom] -- Shorten a Github url with git.io. [custom] is an optional custom shortlink."""
    args = text.split()
    url = args[0]
    custom = args[1] if len(args) > 1 else None

    try:
        return web.shorten(url, custom, 'git.io')
    except web.ServiceError as e:
        return e.message