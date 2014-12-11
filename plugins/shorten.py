from cloudbot import hook
from cloudbot.util import web


@hook.command()
def shorten(text):
    """<url> [custom] - shortens a url with [custom] as an optional custom shortlink"""
    args = text.split()
    url = args[0]
    custom = args[1] if len(args) > 1 else None

    try:
        return web.shorten(url, custom=custom)
    except web.ServiceError as e:
        return e.message


@hook.command
def expand(text):
    """<url> - unshortens <url>"""
    args = text.split()
    url = args[0]

    try:
        return web.expand(url)
    except web.ServiceError as e:
        return e.message


@hook.command()
def isgd(text):
    """<url> [custom] - shortens a url using is.gd with [custom] as an optional custom shortlink,
    or unshortens <url> if already short"""
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
    """<url> [custom] - shorten <url> using goo.gl with [custom] as an option custom shortlink,
    or unshortens <url> if already short"""
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
    """<url> [custom] - shortens a github URL <url> using git.io with [custom] as an optional custom shortlink,
    or unshortens <url> if already short"""
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
