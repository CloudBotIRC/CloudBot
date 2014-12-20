from datetime import datetime
from lxml import html
import re
import random
import requests
import asyncio
import urllib.parse

from cloudbot import hook
from cloudbot.util import timeformat, formatting

reddit_re = re.compile(r'.*(((www\.)?reddit\.com/r|redd\.it)[^ ]+)', re.I)

base_url = "http://reddit.com/r/{}/.json"
short_url = "http://redd.it/{}"


@hook.regex(reddit_re)
def reddit_url(match):

    url = match.group(1)
    if not urllib.parse.urlparse(url).scheme:
        url = "http://" + url

    r = requests.get(url)
    thread = html.fromstring(r.text)

    title = thread.xpath('//title/text()')[0]
    author = thread.xpath("//div[@id='siteTable']//a[contains(@class,'author')]/text()")[0]
    timeago = thread.xpath("//div[@id='siteTable']//p[@class='tagline']/time/text()")[0]
    try:
        comments = thread.xpath("//div[@id='siteTable']//a[@class='comments may-blank']/text()")[0]
    except IndexError:
        comments = thread.xpath("//div[@id='siteTable']//a[@class='comments empty may-blank']/text()")[0]
        if comments == "comment":
            comments = "0 comments"
        else:
            pass
    pointsnum = thread.xpath("//div[@class='score']//span[@class='number']/text()")[0]
    pointsword = thread.xpath("//div[@class='score']//span[@class='word']/text()")[0]

    return '\x02{}\x02 - posted by \x02{}\x02 {} - {} - {} {}'.format(
        title, author, timeago, comments, pointsnum, pointsword)


@asyncio.coroutine
@hook.command(autohelp=False)
def reddit(text, loop):
    """<subreddit> [n] - gets a random post from <subreddit>, or gets the [n]th post in the subreddit"""
    id_num = None

    if text:
        # clean and split the input
        parts = text.lower().strip().split()

        # find the requested post number (if any)
        if len(parts) > 1:
            url = base_url.format(parts[0].strip())
            try:
                id_num = int(parts[1]) - 1
            except ValueError:
                return "Invalid post number."
        else:
            url = base_url.format(parts[0].strip())
    else:
        url = "http://reddit.com/.json"

    try:
        request = yield from loop.run_in_executor(None, requests.get, url)
        data = request.json()
    except Exception as e:
        return "Error: " + str(e)
    data = data["data"]["children"]

    # get the requested/random post
    if id_num is not None:
        try:
            item = data[id_num]["data"]
        except IndexError:
            length = len(data)
            return "Invalid post number. Number must be between 1 and {}.".format(length)
    else:
        item = random.choice(data)["data"]

    item["title"] = formatting.truncate_str(item["title"], 50)
    item["link"] = short_url.format(item["id"])

    raw_time = datetime.fromtimestamp(int(item["created_utc"]))
    item["timesince"] = timeformat.timesince(raw_time)

    if item["over_18"]:
        item["warning"] = " \x02NSFW\x02"
    else:
        item["warning"] = ""

    return "\x02{title} : {subreddit}\x02 - posted by \x02{author}\x02" \
           " {timesince} ago - {score} karma -" \
           " {link}{warning}".format(**item)
