import re
from util import hook, http, web
from util.text import truncate_str
from bs4 import BeautifulSoup, NavigableString, Tag


steam_re = (r'(.*:)//(store.steampowered.com)(:[0-9]+)?(.*)', re.I)


def get_steam_info(url):
    page = http.get(url)
    soup = BeautifulSoup(page, 'lxml', from_encoding="utf-8")

    data = {}

    data["name"] = soup.find('div', {'class': 'apphub_AppName'}).text
    data["desc"] = truncate_str(soup.find('div', {'class': 'game_description_snippet'}).text.strip())

    # get the element details_block
    details = soup.find('div', {'class': 'details_block'})

    # MAGIC
    for b in details.findAll('b'):
        title = b.text.lower().replace(":", "")
        if title == "languages":
            # we have all we need!
            break

        next = b.nextSibling
        if next:
            if isinstance(next, NavigableString):
                text = next.string.strip()
                if text:
                    data[title] = text
                    continue
                else: 
                    next = next.find_next('a', href=True)

            if isinstance(next, Tag) and next.name == 'a':
                text = next.string.strip()
                if text:
                    data[title] = text
                    continue


    data["price"] = soup.find('div', {'class': 'game_purchase_price price'}).text.strip()

    return u"\x02{name}\x02: {desc}, \x02Genre\x02: {genre}, \x02Release Date\x02: {release date}, \x02Price\x02: {price}".format(**data)


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
