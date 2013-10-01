from util import hook, http, web, text


@hook.command("feed")
@hook.command
def rss(inp, message=None):
    """rss <feed> -- Gets the first three items from the RSS feed <feed>."""
    limit = 3

    # preset news feeds
    strip = inp.lower().strip()
    if strip == "bukkit":
        feed = "http://dl.bukkit.org/downloads/craftbukkit/feeds/latest-rb.rss"
        limit = 1
    elif strip == "xkcd":
        feed = "http://xkcd.com/rss.xml"
    elif strip == "ars":
        feed = "http://feeds.arstechnica.com/arstechnica/index"
    else:
        feed = inp

    query = "SELECT title, link FROM rss WHERE url=@feed LIMIT @limit"
    result = web.query(query, {"feed": feed, "limit": limit})

    if not result.rows:
        return "Could not find/read RSS feed."

    for row in result.rows:
        title = text.truncate_str(row["title"], 100)
        try:
            link = web.isgd(row["link"])
        except (web.ShortenError, http.HTTPError, http.URLError):
            link = row["link"]
        message(u"{} - {}".format(title, link))


@hook.command(autohelp=False)
def rb(inp, message=None):
    """rb -- Shows the latest Craftbukkit recommended build"""
    rss("bukkit", message)
