import random

import requests
from lxml import html

from cloudbot import hook
from cloudbot.util import formatting, filesize, colors


API_URL = "https://api.datamarket.azure.com/Bing/Search/v1/Composite"

# filters for SafeSearch
# DEFAULT_FILTER is used unless a user appends " nsfw" to a search term, then the NSFW_FILTER is used
# use ("Moderate", "Off") to allow searching NSFW content with the NSFW search tag
# use ("Strict", "Strict") to block all NSFW content
# the default config just sets the filter to Moderate for all queries
DEFAULT_FILTER = "Moderate"
NSFW_FILTER = "Moderate"


def unescape(s):
    if not s.strip():
        return s
    return html.fromstring(s).text_content()


def bingify(s):
    """ because bing has to be an asshole and require special params """
    return "'{}'".format(s)


@hook.command("bing", "b")
def bing(text, bot):
    """<query> - returns the first bing search result for <query>"""
    api_key = bot.config.get("api_keys", {}).get("bing_azure")

    # handle NSFW
    show_nsfw = text.endswith(" nsfw")
    # remove "nsfw" from the input string after checking for it
    if show_nsfw:
        text = text[:-5].strip().lower()

    rating = NSFW_FILTER if show_nsfw else DEFAULT_FILTER

    if not api_key:
        return "Error: No Bing Azure API details."

    # why are these all differing formats and why does format have a $? ask microsoft
    params = {
        "Sources": bingify("web"),
        "Query": bingify(text),
        "Adult": bingify(rating),
        "$format": "json"
    }

    request = requests.get(API_URL, params=params, auth=(api_key, api_key))

    # I'm not even going to pretend to know why results are in ['d']['results'][0]
    j = request.json()['d']['results'][0]

    if not j["Web"]:
        return "No results."

    result = j["Web"][0]

    # not entirely sure this even needs un-escaping, but it wont hurt to leave it in
    title = formatting.truncate(unescape(result["Title"]), 60)
    desc = formatting.truncate(unescape(result["Description"]), 150)
    url = unescape(result["Url"])

    return colors.parse('{} -- $(b){}$(b): "{}"'.format(url, title, desc))


@hook.command("bingimage", "bis")
def bingimage(text, bot):
    """<query> - returns the first bing image search result for <query>"""
    api_key = bot.config.get("api_keys", {}).get("bing_azure")

    # handle NSFW
    show_nsfw = text.endswith(" nsfw")

    # remove "nsfw" from the input string after checking for it
    if show_nsfw:
        text = text[:-5].strip().lower()

    rating = NSFW_FILTER if show_nsfw else DEFAULT_FILTER

    if not api_key:
        return "Error: No Bing Azure API details."

    # why are these all differing formats and why does format have a $? ask microsoft
    params = {
        "Sources": bingify("image"),
        "Query": bingify(text),
        "Adult": bingify(rating),
        "$format": "json"
    }

    request = requests.get(API_URL, params=params, auth=(api_key, api_key))

    # I'm not even going to pretend to know why results are in ['d']['results'][0]
    j = request.json()['d']['results'][0]

    if not j["Image"]:
        return "No results."

    # grab a random result from the top 10
    result = random.choice(j["Image"][:10])

    # output stuff
    tags = []

    # image size
    tags.append("{}x{}px".format(result["Width"], result["Height"]))
    # file type
    tags.append(result["ContentType"])
    # file size
    tags.append(filesize.size(int(result["FileSize"]), system=filesize.alternative))
    # NSFW warning
    if "explicit" in result["Thumbnail"]["MediaUrl"]:
        tags.append("NSFW")

    # join all the tags together in a comma separated string ("tag1, tag2, tag3")
    tag_text = ", ".join(tags)

    return '{} ({})'.format(unescape(result["MediaUrl"]), tag_text)
