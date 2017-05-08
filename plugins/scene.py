"""
scene.py

Provides commands for searching scene releases using pre.corrupt-net.org.

Created By:
    - Ryan Hitchman <https://github.com/rmmh>

Modified By:
    - Luke Rogers <https://github.com/lukeroge>

Converted to pre.corrupt-net.org By:
    - whocares <http://github.com/whocares-openscene>

License:
    GPL v3
"""

import datetime

import requests
import re
from lxml import html

from cloudbot import hook
from cloudbot.util import timeformat


@hook.command("pre", "scene")
def pre(text):
    """pre <query> -- searches scene releases using pre.corrupt.org"""

    try:
        headers = {'Accept-Language': 'en-US'}
        request = requests.get("https://pre.corrupt-net.org/search.php", params={"search": text}, headers=headers)
        request.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return 'Unable to fetch results: {}'.format(e)
    split = request.text.partition('</tr><tr>')

    results = re.search("<tr><td id\=\"rlstype\".*>(.*)</td><td.*>&nbsp;&nbsp;(.*)<span id\=\"rlsgroup\"><font color\='#C0C0C0'>(.*)</font>.*>(\d*F).*>([\d\.]*M).*&nbsp;&nbsp;(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})</td>", split[0], flags=re.IGNORECASE)
    if results is None:
        return "No results found."

    date = results.group(6)
    section = results.group(1)
    name = results.group(2) + results.group(3)
    size = results.group(5)
    files = results.group(4)

    # parse date/time
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    date_string = date.strftime("%d %b %Y")
    since = timeformat.time_since(date)

    return '{} - {} - {} - {} - {} ({} ago)'.format(section, name, size, files, date_string, since)

