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

# A nice user agent for use with Reddit
headers = {'User-Agent': 'CloudBot/dev 1.0 - CloudBot Refresh'}


def plural(num=0, text=''):
    return "\x02{}\x02 {}{}".format(num, text, "s"[num == 1:])


@hook.regex(reddit_re)
def reddit_url(match):
    url = match.group(1)
    if "redd.it" in url:
        url = "http://" + url
        response = requests.get(url)
        url = response.url + "/.json"
    if not urllib.parse.urlparse(url).scheme:
        url = "http://" + url + "/.json"

    # The Reddit API will not play nice if it doesn't identify with headers...
    r = requests.get(url, headers=headers)
    data = r.json()
    data = data[0]["data"]["children"][0]["data"]
    item = data

    item["title"] = formatting.truncate_str(item["title"], 50)

    raw_time = datetime.fromtimestamp(int(item["created_utc"]))
    item["timesince"] = timeformat.timesince(raw_time)

    item["comments"] = plural(item["num_comments"], 'comment')
    item["points"] = plural(item["score"], 'point')

    if item["over_18"]:
        item["warning"] = " \x02NSFW\x02"
    else:
        item["warning"] = ""

    return "\x02{title}\x02 : \x02{subreddit}\x02 - posted by \x02{author}\x02" \
           " {timesince} ago - {comments}, {points}{warning}".format(**item)


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

    item["title"] = formatting.truncate_str(item["title"], 50)
    item["link"] = short_url.format(item["id"])

    raw_time = datetime.fromtimestamp(int(item["created_utc"]))
    item["timesince"] = timeformat.timesince(raw_time)

    item["comments"] = plural(item["num_comments"], 'comment')
    item["points"] = plural(item["score"], 'point')

    if item["over_18"]:
        item["warning"] = " \x02NSFW\x02"
    else:
        item["warning"] = ""

    return "\x02{title}\x02 : \x02{subreddit}\x02 - posted by \x02{author}\x02" \
           " {timesince} ago - {comments}, {points} -" \
           " {link}{warning}".format(**item)
