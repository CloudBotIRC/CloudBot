"""
scene.py

Provides commands for searching scene releases using orlydb.com.

Created By:
    - Ryan Hitchman <https://github.com/rmmh>

Modified By:
    - Luke Rogers <https://github.com/lukeroge>

License:
    GPL v3
"""

import datetime

import requests
from lxml import html

from cloudbot import hook
from cloudbot.util import timeformat


@hook.command("pre", "scene")
def pre(text):
    """pre <query> -- searches scene releases using orlydb.com"""

    try:
        request = requests.get("http://orlydb.com/", params={"q": text})
        request.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return 'Unable to fetch results: {}'.format(e)

    h = html.fromstring(request.text)

    results = h.xpath("//div[@id='releases']/div/span[@class='release']/..")

    if not results:
        return "No results found."

    result = results[0]

    date = result.xpath("span[@class='timestamp']/text()")[0]
    section = result.xpath("span[@class='section']//text()")[0]
    name = result.xpath("span[@class='release']/text()")[0]

    # parse date/time
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    date_string = date.strftime("%d %b %Y")
    since = timeformat.time_since(date)

    size = result.xpath("span[@class='inforight']//text()")
    if size:
        size = ' - ' + size[0].split()[0]
    else:
        size = ''

    return '{} - {}{} - {} ({} ago)'.format(section, name, size, date_string, since)

