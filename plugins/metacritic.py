import re

import requests
from lxml import html

from cloudbot import hook
from cloudbot.util import web


@hook.command("metacritic", "mc")
def metacritic(text):
    """[all|movie|tv|album|x360|ps3|pc|gba|ds|3ds|wii|vita|wiiu|xone|ps4] <title> - gets rating for <title> from
     metacritic on the specified medium"""

    args = text.strip()

    game_platforms = ('x360', 'ps3', 'pc', 'gba', 'ds', '3ds', 'wii',
                      'vita', 'wiiu', 'xone', 'ps4')

    all_platforms = game_platforms + ('all', 'movie', 'tv', 'album')

    try:
        plat, title = args.split(' ', 1)
        if plat not in all_platforms:
            # raise the ValueError so that the except block catches it
            # in this case, or in the case of the .split above raising the
            # ValueError, we want the same thing to happen
            raise ValueError
    except ValueError:
        plat = 'all'
        title = args

    cat = 'game' if plat in game_platforms else plat

    title_safe = requests.utils.quote(title)

    url = 'http://www.metacritic.com/search/{}/{}/results'.format(cat, title_safe)

    # metacritic thinks it's so damn smart blocking my scraper
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, '
                      'like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Referer':  'http://www.metacritic.com/'
    }

    try:
        request = requests.get(url, headers=headers)
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get Metacritic info: {}".format(e)

    doc = html.fromstring(request.text)

    # get the proper result element we want to pull data from
    result = None

    if not doc.find_class('query_results'):
        return 'No results found.'

    # if they specified an invalid search term, the input box will be empty
    if doc.get_element_by_id('search_term').value == '':
        return 'Invalid search term.'

    if plat not in game_platforms:
        # for [all] results, or non-game platforms, get the first result
        result = doc.find_class('result first_result')[0]

        # find the platform, if it exists
        result_type = result.find_class('result_type')
        if result_type:

            # if the result_type div has a platform div, get that one
            platform_div = result_type[0].find_class('platform')
            if platform_div:
                plat = platform_div[0].text_content().strip()
            else:
                # otherwise, use the result_type text_content
                plat = result_type[0].text_content().strip()

    else:
        # for games, we want to pull the first result with the correct
        # platform
        results = doc.find_class('result')
        for res in results:
            result_plat = res.find_class('platform')[0].text_content().strip()
            if result_plat == plat.upper():
                result = res
                break

    if result is None:
        return 'No results found.'

    # get the name, release date, and score from the result
    product_title = result.find_class('product_title')[0]
    name = product_title.text_content()
    link = 'http://metacritic.com' + product_title.find('a').attrib['href']

    try:
        release = result.find_class('release_date')[0]. \
            find_class('data')[0].text_content()

        # strip extra spaces out of the release date
        release = re.sub(r'\s{2,}', ' ', release)
    except IndexError:
        release = None

    try:
        score = result.find_class('metascore_w')[0].text_content()
    except IndexError:
        score = None

    return '[{}] {} - \x02{}/100\x02, {} - {}'.format(plat.upper(), name, score or 'no score',
                                                      'release: \x02%s\x02' % release if release else 'unreleased',
                                                      link)
