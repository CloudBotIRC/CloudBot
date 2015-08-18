"""
voat.py

A Voat compatibility module, designed to compliment reddit.
Based upon reddit.py

Created By:
    - Foxlet <http://furcode.tk/>

License:
    GNU General Public License (Version 3)
"""

import isodate
import re
import random
import asyncio
import functools

import requests

from cloudbot import hook
from cloudbot.util import timeformat, formatting

voat_re = re.compile(r'.*(((www\.)?voat\.co/v)[^ ]+)', re.I)

base_url = "https://voat.co/api/subversefrontpage?subverse={}"
voat_fill_url = "https://voat.co/v/{}/comments/{}"


def format_output(item, show_url=False):
    """ takes a voat post and returns a formatted string """
    if not item["Title"]:
        item["Title"] = formatting.truncate(item["Linkdescription"], 70)
    else:
        item["Title"] = formatting.truncate(item["Title"], 70)
    item["link"] = voat_fill_url.format(item["Subverse"], item["Id"])

    raw_time = isodate.parse_date(item['Date'])
    item["timesince"] = timeformat.time_since(raw_time, count=1, simple=True)

    item["comments"] = formatting.pluralize(item["CommentCount"], 'comment')
    item["points"] = formatting.pluralize(item["Likes"], 'point')

    if item["Type"] == 2:
        item["warning"] = " \x02Link\x02"
    else:
        item["warning"] = ""

    if show_url:
        return "\x02{Title} : {Subverse}\x02 - {comments}, {points}" \
               " - \x02{Name}\x02 {timesince} ago - {link}{warning}".format(**item)
    else:
        return "\x02{Title} : {Subverse}\x02 - {comments}, {points}" \
               " - \x02{Name}\x02, {timesince} ago{warning}".format(**item)


@hook.regex(voat_re)
def voat_url(match, bot):
    headers = {'User-Agent': bot.user_agent, 'content-type':'text/json'}
    url = match.group(1)
    url = url.split('/')
    print(url)
    url = "https://voat.co/api/singlesubmission?id={}".format(url[4])

    # the voat API gets grumpy if we don't include headers
    r = requests.get(url, headers=headers)
    data = r.json()
    print(data)

    return format_output(data)


@asyncio.coroutine
@hook.command(autohelp=False)
def voat(text, bot, loop):
    """<subverse> [n] - gets a random post from <subverse>, or gets the [n]th post in the subverse"""
    id_num = None
    headers = {'User-Agent': bot.user_agent, 'content-type':'text/json'}

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
        url = "https://voat.co/api/frontpage"

    try:
        # Again, identify with Voat using an User Agent
        inquiry = yield from loop.run_in_executor(None, functools.partial(requests.get, url, headers=headers))
        data = inquiry.json()
    except Exception as e:
        return "Error: " + str(e)

    # get the requested/random post
    if id_num is not None:
        try:
            item = data[id_num]
        except IndexError:
            length = len(data)
            return "Invalid post number. Number must be between 1 and {}.".format(length)
    else:
        item = random.choice(data)

    return format_output(item, show_url=True)
