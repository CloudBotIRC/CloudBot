import re

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

from cloudbot import hook
from cloudbot.util import web
from cloudbot.util.formatting import truncate_str


class SteamError(Exception):
    pass


steam_re = re.compile(r'(.*:)//(store.steampowered.com)(:[0-9]+)?(.*)', re.I)


def get_data(url):
    """
    takes a URL to a steam store page and returns a dict of info
    :param url: string
    :return: dict
    """
    try:
        request = requests.get(url)
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise SteamError("Could not get game info: {}".format(e))

    soup = BeautifulSoup(request.text, 'lxml', from_encoding="utf-8")

    data = {"name": soup.find('div', {'class': 'apphub_AppName'}).text,
            "desc": truncate_str(soup.find('meta', {'name': 'description'})['content'].strip(), 80)}

    # get the element details_block
    details = soup.find('div', {'class': 'details_block'})

    # the following code parses over each bit of data in details_block
    # and appends it to the data dict
    for b in details.findAll('b'):
        # get the contents of the <b></b> tag, which is our title
        title = b.text.lower().replace(":", "")
        if title == "languages":
            # we have all we need!
            break

        # find the next element directly after the <b></b> tag
        next_element = b.nextSibling
        if next_element:
            # if the element is some text
            if isinstance(next_element, NavigableString):
                text = next_element.string.strip()
                if text:
                    # we found valid text, save it and continue the loop
                    data[title] = text
                    continue
                else:
                    # the text is blank - sometimes this means there are
                    # useless spaces or tabs between the <b> and <a> tags.
                    # so we find the next <a> tag and carry on to the next
                    # bit of code below
                    next_element = next_element.find_next('a', href=True)

            # if the element is an <a></a> tag
            if isinstance(next_element, Tag) and next_element.name == 'a':
                text = next_element.string.strip()
                if text:
                    # we found valid text (in the <a></a> tag),
                    # save it and continue the loop
                    data[title] = text
                    continue

    price_div = soup.find('div', {'class': 'game_purchase_action_bg'})

    if price_div.find('div', {'class': 'discount_block game_purchase_discount'}):
        data["discounted"] = True
        data["price"] = price_div.find('div', {'class': 'discount_final_price'}).text.strip()
        data["price_original"] = price_div.find('div', {'class': 'discount_original_price'}).text.strip()
    else:
        data["discounted"] = False
        data["price"] = price_div.find('div', {'class': 'game_purchase_price price'}).text.strip()
        data["price_original"] = data["price"]

    data["genre"] = data["genre"].lower()

    return data


@hook.regex(steam_re)
def steam_url(match):
    data = get_data("http://store.steampowered.com" + match.group(4))

    if data["discounted"]:
        return "\x02{name}\x02 - {desc} - \x02{genre}\x02 - released \x02{release date}\x02" \
               " - \x02{price}\x02 (was \x02{price_original}\x02)".format(**data)
    else:
        return "\x02{name}\x02 - {desc} - \x02{genre}\x02 - released \x02{release date}\x02" \
               " - \x02{price}\x02".format(**data)


@hook.command()
def steam(text):
    """steam [search] - Search for specified game/trailer/DLC"""
    params = {'term': text.strip().lower()}

    try:
        request = requests.get("http://store.steampowered.com/search/", params=params)
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get game info: {}".format(e)

    soup = BeautifulSoup(request.text, 'lxml', from_encoding="utf-8")
    result = soup.find('a', {'class': 'search_result_row'})

    if not result:
        return "No game found."

    data = get_data(result['href'])
    data["short_url"] = web.try_shorten(result['href'])

    if data["discounted"]:
        return "\x02{name}\x02 - {desc} - \x02{genre}\x02 - released \x02{release date}\x02" \
               " - \x02{price}\x02 (was \x02{price_original}\x02) - {short_url}".format(**data)
    else:
        return "\x02{name}\x02 - {desc} - \x02{genre}\x02 - released \x02{release date}\x02" \
               " - \x02{price}\x02 - {short_url}".format(**data)
