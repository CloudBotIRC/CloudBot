from cloudbot import hook, http, web


@hook.command
def shorten(text):
    """shorten <url> - Makes an is.gd shortlink to the url provided."""

    try:
        return web.isgd(text)
    except (web.ShortenError, http.HTTPError) as error:
        return error
