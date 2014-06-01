import time
import random

from cloudbot import hook, http, web


## CONSTANTS
from cloudbot import formatting

base_url = "http://api.bukget.org/3/"

search_url = base_url + "search/plugin_name/like/{}"
random_url = base_url + "plugins/bukkit/?start={}&size=1"
details_url = base_url + "plugins/bukkit/{}"


@hook.onload()
def load_categories():
    global categories, count_total, count_categories
    categories = http.get_json("http://api.bukget.org/3/categories")

    count_total = sum([cat["count"] for cat in categories])
    count_categories = {cat["name"].lower(): int(cat["count"]) for cat in categories}  # dict comps!


class BukgetError(Exception):
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        return self.text


## DATA FUNCTIONS

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


def plugin_random():
    """ gets a random plugin from the bukget API and returns the slug """
    results = None

    while not results:
        plugin_number = random.randint(1, count_total)
        print("trying {}".format(plugin_number))
        try:
            results = http.get_json(random_url.format(plugin_number))
        except (http.HTTPError, http.URLError) as e:
            raise BukgetError(500, "Error Fetching Search Page: {}".format(e))

    return results[0]["slug"]


def plugin_details(slug):
    """ takes a plugin slug and returns details from the bukget API """
    slug = slug.lower().strip()

    try:
        details = http.get_json(details_url.format(slug))
    except (http.HTTPError, http.URLError) as e:
        raise BukgetError(500, "Error Fetching Details: {}".format(e))
    return details


## OTHER FUNCTIONS

def format_output(data):
    """ takes plugin data and returns two strings representing information about that plugin """
    name = data["plugin_name"]
    description = formatting.truncate_str(data['description'], 30)
    url = data['website']
    authors = data['authors'][0]
    authors = authors[0] + "\u200b" + authors[1:]
    stage = data['stage']

    current_version = data['versions'][0]

    last_update = time.strftime('%d %B %Y %H:%M',
                                time.gmtime(current_version['date']))
    version_number = data['versions'][0]['version']

    bukkit_versions = ", ".join(current_version['game_versions'])
    link = web.try_shorten(current_version['link'])

    if description:
        line_a = "\x02{}\x02, by \x02{}\x02 - {} - ({}) \x02{}".format(name, authors, description, stage, url)
    else:
        line_a = "\x02{}\x02, by \x02{}\x02 ({}) \x02{}".format(name, authors, stage, url)

    line_b = "Last release: \x02v{}\x02 for \x02{}\x02 at {} \x02{}\x02".format(version_number, bukkit_versions,
                                                                                last_update, link)

    return line_a, line_b


## HOOK FUNCTIONS

@hook.command(["bukget", "plugin"])
def bukget(text, reply, message):
    """<slug/name> - gets details on a plugin from dev.bukkit.org"""
    # get the plugin slug using search
    try:
        slug = plugin_search(text)
    except BukgetError as e:
        return e

    # get the plugin info using the slug
    try:
        data = plugin_details(slug)
    except BukgetError as e:
        return e

    # format the final message and send it to IRC
    line_a, line_b = format_output(data)

    reply(line_a)
    message(line_b)


@hook.command(autohelp=None)
def randomplugin(reply, message):
    """- gets details on a random plugin from dev.bukkit.org"""
    # get a random plugin slug
    try:
        slug = plugin_random()
    except BukgetError as e:
        return e

    # get the plugin info using the slug
    try:
        data = plugin_details(slug)
    except BukgetError as e:
        return e

    # format the final message and send it to IRC
    line_a, line_b = format_output(data)

    reply(line_a)
    message(line_b)
