import re

from bs4 import BeautifulSoup, NavigableString, Tag

from util import hook, http, web
from util.text import truncate_str


steam_re = (r'(.*:)//(store.steampowered.com)(:[0-9]+)?(.*)', re.I)


def get_steam_info(url):
    page = http.get(url)
    soup = BeautifulSoup(page, 'lxml', from_encoding="utf-8")

    data = {}

    data["name"] = soup.find('div', {'class': 'apphub_AppName'}).text
    data["desc"] = truncate_str(soup.find('meta', {'name': 'description'})['content'].strip(), 80)

    # get the element details_block
    details = soup.find('div', {'class': 'details_block'})

    # loop over every <b></b> tag in details_block
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

    data["price"] = soup.find('div', {'class': 'game_purchase_price price'}).text.strip()

    return u"\x02{name}\x02: {desc}, \x02Genre\x02: {genre}, \x02Release Date\x02: {release date}," \
           u" \x02Price\x02: {price}".format(**data)


@hook.regex(*steam_re)
def steam_url(match):
    return get_steam_info("http://store.steampowered.com" + match.group(4))


@hook.command
def steam(inp):
    """steam [search] - Search for specified game/trailer/DLC"""
    page = http.get("http://store.steampowered.com/search/?term=" + inp)
    soup = BeautifulSoup(page, 'lxml', from_encoding="utf-8")
    result = soup.find('a', {'class': 'search_result_row'})
    return get_steam_info(result['href']) + " - " + web.isgd(result['href'])
