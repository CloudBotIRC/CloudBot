from cloudbot import hook, web

@hook.command
def isgd(text):
    """isgd <url> [custom] - Shorten a url with is.gd. [custom] is an optional custom shortlink."""
    args   = text.split()
    url    = args[0]
    custom = args[1] if len(args) > 1 else None
    
    isgd = web.Isgd()
    try:
        return isgd.shorten(url, custom)
    except web.ShortenError as e:
        return e.message

@hook.command
def gitio(text):
    """gitio <url> [custom] -- Shorten a Github url with git.io. [custom] is an optional custom shortlink."""
    args   = text.split()
    url    = args[0]
    custom = args[1] if len(args) > 1 else None
    
    gitio = web.Gitio()
    try:
        return gitio.shorten(url, custom)
    except web.ShortenError as e:
        return e.message