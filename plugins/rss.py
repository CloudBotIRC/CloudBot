from util import hook, web


@hook.command("feed")
@hook.command
def rss(inp, say=None):

    # preset news feeds
    strip = inp.lower().strip()
    if strip == "bukkit":
        feed = "http://dl.bukkit.org/downloads/craftbukkit/feeds/latest-rb.rss"
        limit = 1
    elif strip == "xkcd":
        feed = "http://xkcd.com/rss.xml"
        limit = 2
    else:
        feed = inp
        limit = 3

    query = "SELECT title, link FROM rss WHERE url=@feed LIMIT @limit"
    result = web.query(query, {"feed": feed, "limit": limit or 3})
    for row in result.rows:
        link = web.isgd(row["link"])
        say(u"{} - {}".format(row["title"], link))


@hook.command
def rb(inp, say=None):
    rss("bukkit", say)