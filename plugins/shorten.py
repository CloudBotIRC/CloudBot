from util import hook, http, web


@hook.command
def shorten(inp):
    """shorten <url> - Makes an is.gd shortlink to the url provided."""

    try:
        return web.isgd(inp)
    except (web.ShortenError, http.HTTPError) as error:
        return error
