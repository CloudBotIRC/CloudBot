from util import hook, http, web
import time

base_url = "http://api.bukget.org/3/"

search_url = base_url + "search/plugin_name/like/{}"
details_url = base_url + "plugins/bukkit/{}"

categories = http.get_json("http://api.bukget.org/3/categories")
total_plugins = sum([cat["count"] for cat in categories])


class BukgetError(Exception):
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        return self.text


def plugin_search(term):
    """ searches for a plugin with the bukget API and returns the slug """
    term = term.lower().strip()

    search_term = http.quote_plus(term)

    try:
        results = http.get_json(search_url.format(search_term))
    except (http.HTTPError, http.URLError) as e:
        raise BukgetError(500, "Error Fetching Search Page: {}".format(e))
    
    if not results:
        raise BukgetError(404, "No Results Found")

    for result in results:
        if result["slug"] == term:
            return result["slug"]

    return results[0]["slug"]


def plugin_details(slug):
    """ takes a plugin slug and returns details from the bukget API """
    slug = slug.lower().strip()

    try:
        details = http.get_json(details_url.format(slug))
    except (http.HTTPError, http.URLError) as e:
        raise BukgetError(500, "Error Fetching Details: {}".format(e))
    return details



@hook.command('plugin')
@hook.command
def bukkitplugin(inp, reply=None, message=None):
    """plugin <slug/name> - Look up a plugin on dev.bukkit.org"""
    # get the plugin slug using search
    print total_plugins
    try:
        slug = plugin_search(inp)
    except BukgetError as e:
        return e

    # get the plugin info using the slug
    try:
        data = plugin_details(slug)
    except BukgetError as e:
        return e


    name = data["plugin_name"]
    description = data['description']
    url = data['website']
    authors = data['authors'][0]
    authors = authors[0] + u"\u200b" + authors[1:]
    stage = data['stage']

    current_version = data['versions'][0]

    last_update = time.strftime('%d %B %Y %H:%M',
                               time.gmtime(current_version['date']))
    version_number = data['versions'][0]['version']

    bukkit_versions = ", ".join(current_version['game_versions'])
    link = web.try_isgd(current_version['link'])

    if description:
        reply(u"\x02{}\x02, by \x02{}\x02 - {} - ({}) \x02{}".format(name, authors, description, stage, url))
    else:
        reply(u"\x02{}\x02, by \x02{}\x02 ({}) \x02{}".format(name, authors, stage, url))

    message(u"Last release: \x02v{}\x02 for \x02{}\x02 at {} \x02{}\x02".format(version_number, bukkit_versions, last_update, link))
