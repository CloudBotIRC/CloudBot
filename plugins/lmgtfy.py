from cloudbot import hook, web, http


@hook.command(["lmgtfy", "gfy"])
def lmgtfy(text):
    """lmgtfy [phrase] - Posts a google link for the specified phrase"""

    link = "http://lmgtfy.com/?q={}".format(http.quote_plus(text))

    return web.try_shorten(link)
