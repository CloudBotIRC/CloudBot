from util import hook, web, http


@hook.command('gfy')
@hook.command
def lmgtfy(inp):
    """lmgtfy [phrase] - Posts a google link for the specified phrase"""

    link = u"http://lmgtfy.com/?q={}".format(http.quote_plus(inp))

    try:
        return web.isgd(link)
    except (web.ShortenError, http.HTTPError):
        return link
