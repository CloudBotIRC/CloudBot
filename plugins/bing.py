import random
import requests

from lxml import html

from cloudbot import hook
from cloudbot.util import formatting


API_URL = "https://api.datamarket.azure.com/Bing/Search/v1/Composite"


def unescape(s):
    if not s.strip():
        return s
    return html.fromstring(s).text_content()


def bingify(s):
    """ because bing has to be an asshole and require special params """
    _s = requests.utils.quote(s)
    return "'{}'".format(_s)


@hook.command("bing", "google", "g", "search")
def bing(text, bot):
    """<query> - returns the first bing search result for <query>"""
    api_key = bot.config.get("api_keys", {}).get("bing_azure")

    if not api_key:
        return "Error: No Bing Azure API details."

    # why are these all differing formats and why does format have a $? ask microsoft
    params = {
        "Sources": bingify("web"),
        "Query": bingify(text),
        "$format": "json"
    }

    request = requests.get(API_URL, params=params, auth=(api_key, api_key))

    # I'm not even going to pretend to know why results are in ['d']['results'][0]
    j = request.json()['d']['results'][0]

    if not j["Web"]:
        return "No results."

    result = j["Web"][0]

    # not entirely sure this even needs un-escaping, but it wont hurt to leave it in
    title = formatting.truncate_str(unescape(result["Title"]), 60)
    desc = formatting.truncate_str(unescape(result["Description"]), 150)
    url = unescape(result["Url"])

    return '{} -- \x02{}\x02: "{}"'.format(url, title, desc)


@hook.command("bingimage", "googleimage", "gis", "image")
def bingimage(text, bot):
    """<query> - returns the first bing image search result for <query>"""
    api_key = bot.config.get("api_keys", {}).get("bing_azure")

    if not api_key:
        return "Error: No Bing Azure API details."

    # why are these all differing formats and why does format have a $? ask microsoft
    params = {
        "Sources": bingify("image"),
        "Query": bingify(text),
        "$format": "json"
    }

    request = requests.get(API_URL, params=params, auth=(api_key, api_key))

    # I'm not even going to pretend to know why results are in ['d']['results'][0]
    j = request.json()['d']['results'][0]

    if not j["Image"]:
        return "No results."

    result = random.choice(j["Image"][:10])

    width = result["Width"]
    height = result["Height"]
    url = unescape(result["MediaUrl"])

    return '{} (\x02{}\x02x\x02{}\x02)'.format(url, width, height)
