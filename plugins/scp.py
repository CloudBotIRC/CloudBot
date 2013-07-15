# -*- coding: utf-8 -*-
from util import hook, http
import re


def api_get(kind, query):
    """Use the RESTful Google Search API"""
    url = 'http://ajax.googleapis.com/ajax/services/search/%s?' \
          'v=1.0&safe=moderate'
    return http.get_json(url % kind, q=query)


def get_info(url):
    try:
        page = http.get(url)
    except Exception as e:
        return "Could not get SCP information: Unable to fetch URL. ({})".format(e)
    contents = re.sub('<[^<]+?>', '', page)

    try:
        item_id = http.unescape(re.findall("Item #: (.+?)\n", contents, re.S)[0])
        object_class = http.unescape(re.findall("Object Class: (.+?)\n", contents, re.S)[0])
        description = http.unescape(re.findall("Description: (.+?)\n", contents, re.S)[0])
    except IndexError as e:
        return "Could not get SCP information: Page was not a valid SCP page."

    return u"\x02Item Name:\x02 COMING SOON, \x02Item #:\x02 {}, \x02Class\x02: {}," \
           " \x02Description:\x02 {}.".format(item_id, object_class, description)


@hook.command
def scp(inp):
    "scp <query>/<item id> -- Returns SCP Foundation wiki search result for <query>/<item id>."

    if not inp.isdigit():
        term = inp
    else:
        if len(inp) == 3:
            term = inp
        if len(inp) == 2:
            term = "0" + inp
        if len(inp) == 1:
            term = "00" + inp

    # search for the SCP on google
    search_term = "site:scp-wiki.net {}".format(term)
    parsed = api_get("web", search_term)
    if not parsed['responseData']['results']:
        return 'Could not get SCP information: No results found.'
    result = parsed['responseData']['results'][0]
    url = result['unescapedUrl']

    return get_info(url)
