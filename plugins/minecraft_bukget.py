import time
import random

import requests

from cloudbot import hook
from cloudbot.util import web, formatting


# # CONSTANTS

base_url = "http://api.bukget.org/3/"

search_url = base_url + "search/plugin_name/like/{}"
random_url = base_url + "plugins/bukkit/?start={}&size=1"
details_url = base_url + "plugins/bukkit/{}"


@hook.on_start()
def load_categories():
    global categories, count_total, count_categories
    categories = requests.get("http://api.bukget.org/3/categories").json()

    count_total = sum([cat["count"] for cat in categories])
    count_categories = {cat["name"].lower(): int(cat["count"]) for cat in categories}  # dict comps!


class BukgetError(Exception):
    pass


# DATA FUNCTIONS

def plugin_search(term):
    """ searches for a plugin with the bukget API and returns the slug """
    term = term.lower().strip()

    search_term = requests.utils.quote(term)

    try:
        request = requests.get(search_url.format(search_term))
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise BukgetError("Error Fetching Search Page: {}".format(e))

    try:
        results = request.json()
    except ValueError:
        raise BukgetError("Error Parsing Search Page")

    if not results:
        raise BukgetError("No Results Found")

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
            request = requests.get(random_url.format(plugin_number))
            request.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            raise BukgetError("Error Fetching Search Page: {}".format(e))

        try:
            results = request.json()
        except ValueError:
            raise BukgetError("Error Parsing Search Page")

    return results[0]["slug"]


def plugin_details(slug):
    """ takes a plugin slug and returns details from the bukget API """
    slug = slug.lower().strip()

    try:
        request = requests.get(details_url.format(slug))
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise BukgetError("Error Fetching Details: {}".format(e))

    try:
        details = request.json()
    except ValueError:
        raise BukgetError("Error Parsing Details")

    return details


# OTHER FUNCTIONS

def format_output(data):
    """ takes plugin data and returns two strings representing information about that plugin """
    name = data["plugin_name"]
    description = formatting.truncate(data['description'], 30)
    url = data['website']
    if data['authors']:
        authors = data['authors'][0]
        authors = authors[0] + "\u200b" + authors[1:]
    else:
        authors = "Unknown"

    stage = data['stage']

    current_version = data['versions'][0]

    last_update = time.strftime('%d %B %Y %H:%M',
                                time.gmtime(current_version['date']))
    version_number = data['versions'][0]['version']

    bukkit_versions = ", ".join(current_version['game_versions'])
    link = web.try_shorten(current_version['link'])

    if description:
        line_a = "\x02{}\x02, by \x02{}\x02 - {} - ({}) - {}".format(name, authors, description, stage, url)
    else:
        line_a = "\x02{}\x02, by \x02{}\x02 ({}) - {}".format(name, authors, stage, url)

    line_b = "Last release: \x02v{}\x02 for \x02{}\x02 at {} - {}".format(version_number, bukkit_versions,
                                                                          last_update, link)

    return line_a, line_b


# HOOK FUNCTIONS

@hook.command("bukget", "plugin")
def bukget(text):
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
    return format_output(data)


@hook.command(autohelp=None)
def randomplugin():
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
    return format_output(data)

