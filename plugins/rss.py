from cloudbot import hook
from cloudbot.util import formatting, web


@hook.command("feed")
@hook.command()
def rss(text, message):
    """rss <feed> -- Gets the first three items from the RSS feed <feed>."""
    limit = 3

    # preset news feeds
    strip = text.lower().strip()
    if strip == "xkcd":
        feed = "http://xkcd.com/rss.xml"
    elif strip == "ars":
        feed = "http://feeds.arstechnica.com/arstechnica/index"
    else:
        feed = text

    query = "SELECT title, link FROM rss WHERE url=@feed LIMIT @limit"
    result = web.query(query, {"feed": feed, "limit": limit})

    if not result.rows:
        return "Could not find/read RSS feed."

    for row in result.rows:
        title = formatting.truncate_str(row["title"], 100)
        link = web.try_shorten(row["link"])
        message("{} - {}".format(title, link))
