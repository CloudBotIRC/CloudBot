from datetime import datetime
import re
import random
import asyncio
import functools
import urllib.parse

import requests

from cloudbot import hook
from cloudbot.util import timeformat, formatting


reddit_re = re.compile(r'.*(((www\.)?reddit\.com/r|redd\.it)[^ ]+)', re.I)

base_url = "http://reddit.com/r/{}/.json"
short_url = "http://redd.it/{}"


def format_output(item, show_url=False):
    """ takes a reddit post and returns a formatted string """
    item["title"] = formatting.truncate(item["title"], 70)
    item["link"] = short_url.format(item["id"])

    raw_time = datetime.fromtimestamp(int(item["created_utc"]))
    item["timesince"] = timeformat.time_since(raw_time, count=1, simple=True)

    item["comments"] = formatting.pluralize(item["num_comments"], 'comment')
    item["points"] = formatting.pluralize(item["score"], 'point')

    if item["over_18"]:
        item["warning"] = " \x02NSFW\x02"
    else:
        item["warning"] = ""

    if show_url:
        return "\x02{title} : {subreddit}\x02 - {comments}, {points}" \
               " - \x02{author}\x02 {timesince} ago - {link}{warning}".format(**item)
    else:
        return "\x02{title} : {subreddit}\x02 - {comments}, {points}" \
               " - \x02{author}\x02, {timesince} ago{warning}".format(**item)


@hook.regex(reddit_re)
def reddit_url(match, bot):
    url = match.group(1)
    if "redd.it" in url:
        url = "http://" + url
        response = requests.get(url)
        url = response.url + "/.json"
    if not urllib.parse.urlparse(url).scheme:
        url = "http://" + url + "/.json"

    # the reddit API gets grumpy if we don't include headers
    headers = {'User-Agent': bot.user_agent}
    r = requests.get(url, headers=headers)
    data = r.json()
    item = data[0]["data"]["children"][0]["data"]

    return format_output(item)


@asyncio.coroutine
@hook.command(autohelp=False)
def reddit(text, bot, loop):
    """<subreddit> [n] - gets a random post from <subreddit>, or gets the [n]th post in the subreddit"""
    id_num = None
    headers = {'User-Agent': bot.user_agent}

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
        # Again, identify with Reddit using an User Agent, otherwise get a 429
        inquiry = yield from loop.run_in_executor(None, functools.partial(requests.get, url, headers=headers))
        data = inquiry.json()
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

    return format_output(item, show_url=True)
