import feedparser

from cloudbot import hook
from cloudbot.util import web, formatting


def format_item(item):
    url = web.try_shorten(item.link)
    title = formatting.strip_html(item.title)
    return "{} ({})".format(
        title, url)


@hook.command("feed", "rss", "news")
def rss(text):
    """<feed> -- Gets the first three items from the RSS/ATOM feed <feed>."""
    limit = 3

    text = text.lower().strip()
    if text == "xkcd":
        addr = "http://xkcd.com/rss.xml"
    elif text == "ars":
        addr = "http://feeds.arstechnica.com/arstechnica/index"
    elif text == "world":
        addr = "https://news.google.com/news?cf=all&ned=us&hl=en&topic=w&output=rss"
    elif text in ("us", "usa"):
        addr = "https://news.google.com/news?cf=all&ned=us&hl=en&topic=n&output=rss"
    elif text == "nz":
        addr = "https://news.google.com/news?pz=1&cf=all&ned=nz&hl=en&topic=n&output=rss"
    elif text in ("anand", "anandtech"):
        addr = "http://www.anandtech.com/rss/"
    else:
        addr = text

    feed = feedparser.parse(addr)
    if not feed.entries:
        return "Feed not found."

    out = []
    for item in feed.entries[:limit]:
        out.append(format_item(item))

    start = "\x02{}\x02: ".format(feed.feed.title) if 'title' in feed.feed else ""
    return start + ", ".join(out)
