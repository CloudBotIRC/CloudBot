from cloudbot import hook
from cloudbot.util import web, formatting
import re
import requests

from bs4 import BeautifulSoup

SCP_SEARCH = "http://www.scp-wiki.net/search:site/q/{}"


def search(query):
    """Takes an SCP name and returns a link"""
    request = requests.get(SCP_SEARCH.format(query))
    soup = BeautifulSoup(request.content)

    results = soup.find('div', {'class': 'search-results'})
    if "no results" in results.get_text():
        return None

    item = results.find('div', {'class': 'item'})
    return item.find('div', {'class': 'url'}).get_text().strip()


def get_title(scp_id):
    """ An insanely over-complicated function that gets the name of a SCP, because the SCP page does not
    include the name (?!?!?! WHY)
    """
    # get the page
    if "J" in scp_id:
        page = "http://www.scp-wiki.net/joke-scps"
    elif "ARC" in scp_id:
        page = "http://www.scp-wiki.net/archived-scps"
    elif "D" in scp_id:
        page = "http://www.scp-wiki.net/decommissioned-scps"
    elif "EX" in scp_id:
        page = "http://www.scp-wiki.net/scp-ex"
    else:
        try:
            stripped_id = scp_id[4:]
            int_id = int(stripped_id)
        except ValueError:
            return None

        if int_id < 1000:
            page = "http://www.scp-wiki.net/scp-series"
        elif int_id >= 100 < 2000:
            page = "http://www.scp-wiki.net/scp-series-2"
        elif int_id >= 2000 < 3000:
            page = "http://www.scp-wiki.net/scp-series-3"
        else:
            return None

    # get the name
    try:
        request = requests.get(page)
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        return None

    soup = BeautifulSoup(request.content)
    item = soup.find(text=scp_id)

    if not item:
        return None

    try:
        name = item.parent.parent.contents[1][3:].strip()
    except:
        return None
    return name


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

    title = get_title(item_id)

    if not title:
        title = "Unknown"

    return "\x02Item Name:\x02 {}, \x02Item #:\x02 {}, \x02Class\x02: {}," \
           " \x02Description:\x02 {} - {}".format(title, item_id, object_class, description, short_url)




@hook.command
def scp(text):
    """scp <query>/<item id> -- Returns SCP Foundation wiki search result for <query>/<item id>."""

    if not text.isdigit():
        term = text
    else:
        if len(text) == 3:
            term = text
        if len(text) == 2:
            term = "0" + text
        if len(text) == 1:
            term = "00" + text

    # search for the SCP
    url = search(term)

    if not url:
        return "Could not get SCP information: No results found."

    return get_info(url)
