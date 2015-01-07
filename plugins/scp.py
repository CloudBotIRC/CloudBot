import re
import asyncio

import requests
from bs4 import BeautifulSoup

from cloudbot import hook
from cloudbot.util import web, formatting


SCP_SEARCH = "http://www.scp-wiki.net/search:site/q/{}"
NAME_LISTS = ["http://www.scp-wiki.net/joke-scps", "http://www.scp-wiki.net/archived-scps",
              "http://www.scp-wiki.net/decommissioned-scps", "http://www.scp-wiki.net/scp-ex",
              "http://www.scp-wiki.net/scp-series", "http://www.scp-wiki.net/scp-series-2",
              "http://www.scp-wiki.net/scp-series-3"]

scp_cache = {}


@asyncio.coroutine
@hook.command
def load_names(loop):
    """ creates a SCP-ID > NAME/URL mapping """
    for url in NAME_LISTS:
        request = yield from loop.run_in_executor(None, requests.get, url)
        soup = BeautifulSoup(request.text)

        page = soup.find('div', {'id': 'page-content'}).find('div', {'class': 'content-panel standalone series'})
        names = page.find_all("a", text=re.compile(r"SCP-"))

        for item in names:
            scp_id = item.text
            name = item.parent.contents[1][3:].strip()
            url = item['href']
            data = (name, url)

            scp_cache[scp_id] = data


@asyncio.coroutine
@hook.onload()
def initial_refresh(loop):
    # do an initial refresh of the caches
    yield from load_names(loop)


def search(query):
    """Takes an SCP name and returns a link"""
    # we see if the query is an SCPID in our pre-generated cache
    if query.upper() in scp_cache:
        return "http://www.scp-wiki.net" + scp_cache[query.upper()][1]

    request = requests.get(SCP_SEARCH.format(query))
    soup = BeautifulSoup(request.content)

    results = soup.find('div', {'class': 'search-results'})
    if "no results" in results.get_text():
        return None

    item = results.find('div', {'class': 'item'})
    return item.find('div', {'class': 'url'}).get_text().strip()


def get_info(url):
    """ Takes a SCPWiki URL and returns a formatted string """
    try:
        request = requests.get(url)
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get SCP information: Unable to fetch URL. ({})".format(e)
    html = request.text
    contents = formatting.strip_html(html)

    try:
        item_id = re.findall("Item #: (.+?)\n", contents, re.S)[0]
        object_class = re.findall("Object Class: (.+?)\n", contents, re.S)[0]
        description = re.findall("Description: (.+?)\n", contents, re.S)[0]
    except IndexError:
        return "Could not get SCP information: Page was not a valid SCP page."

    description = formatting.truncate_str(description, 150)
    short_url = web.try_shorten(url)

    # get the title from our pre-generated cache
    if item_id in scp_cache:
        title = scp_cache[item_id][0]
    else:
        title = "Unknown"

    return "\x02Item Name:\x02 {}, \x02Item #:\x02 {}, \x02Class\x02: {}," \
           " \x02Description:\x02 {} - {}".format(title, item_id, object_class, description, short_url)


@hook.command
def scp(text):
    """scp <query>/<item id> -- Returns SCP Foundation wiki search result for <query>/<item id>."""
    if not text.isdigit():
        term = text
    else:
        if len(text) == 4:
            term = "SCP-" + text
        elif len(text) == 3:
            term = "SCP-" + text
        elif len(text) == 2:
            term = "SCP-0" + text
        elif len(text) == 1:
            term = "SCP-00" + text
        else:
            term = text

    # search for the SCP
    url = search(term)

    if not url:
        return "Could not get SCP information: No results found."

    return get_info(url)
