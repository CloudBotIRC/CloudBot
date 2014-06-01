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
def expand(text):
    """expand <url> - Expand a url."""
    args = text.split()
    url = args[0]

    try:
        return web.expand(url)
    except web.ServiceError as e:
        return e.message


@hook.command
def isgd(text):
    """isgd <url> [custom] - Shorten/unshorten <url> with is.gd. [custom] is an optional custom shortlink."""
    args = text.split()
    url = args[0]
    custom = args[1] if len(args) > 1 else None

    try:
        if 'is.gd' in url:
            return web.expand(url, 'is.gd')
        else:
            return web.shorten(url, custom, 'is.gd')
    except web.ServiceError as e:
        return e.message


@hook.command
def googl(text):
    """googl <url> - Shorten/unshorten <url> with goo.gl."""
    args = text.split()
    url = args[0]
    custom = args[1] if len(args) > 1 else None

    try:
        if 'goo.gl' in url:
            return web.expand(url, 'goo.gl')
        else:
            return web.shorten(url, custom, 'goo.gl')
    except web.ServiceError as e:
        return e.message


@hook.command
def gitio(text):
    """gitio <url> [custom] -- Shorten/unshorten <url> with git.io. [custom] is an optional custom shortlink."""
    args = text.split()
    url = args[0]
    custom = args[1] if len(args) > 1 else None

    try:
        if 'git.io' in url:
            return web.expand(url, 'git.io')
        else:
            return web.shorten(url, custom, 'git.io')
    except web.ServiceError as e:
        return e.message