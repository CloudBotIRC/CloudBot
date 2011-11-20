# metacritic.com scraper

import re
from urllib2 import HTTPError

from util import hook, http


@hook.command('mc')
def metacritic(inp):
    '.mc [all|movie|tv|album|x360|ps3|pc|ds|wii] <title> -- gets rating for'\
    ' <title> from metacritic on the specified medium'

    # if the results suck, it's metacritic's fault

    args = inp.strip()

    game_platforms = ('x360', 'ps3', 'pc', 'ds', 'wii', '3ds', 'gba')
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

    title_safe = http.quote_plus(title)

    url = 'http://www.metacritic.com/search/%s/%s/results' % (cat, title_safe)

    try:
        doc = http.get_html(url)
    except HTTPError:
        return 'error fetching results'

    ''' result format:
    -- game result, with score
    -- subsequent results are the same structure, without first_result class
    <li class="result first_result">
        <div class="result_type">
            <strong>Game</strong>
            <span class="platform">WII</span>
        </div>
        <div class="result_wrap">
            <div class="basic_stats has_score">
                <div class="main_stats">
                    <h3 class="product_title basic_stat">...</h3>
                    <div class="std_score">
                      <div class="score_wrap">
                        <span class="label">Metascore: </span>
                        <span class="data metascore score_favorable">87</span>
                      </div>
                    </div>
                </div>
                <div class="more_stats extended_stats">...</div>
            </div>
        </div>
    </li>

    -- other platforms are the same basic layout
    -- if it doesn't have a score, there is no div.basic_score
    -- the <div class="result_type"> changes content for non-games:
    <div class="result_type"><strong>Movie</strong></div>
    '''

    # get the proper result element we want to pull data from

    result = None

    if not doc.find_class('query_results'):
        return 'no results found'

    # if they specified an invalid search term, the input box will be empty
    if doc.get_element_by_id('search_term').value == '':
        return 'invalid search term'

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

    if not result:
        return 'no results found'

    # get the name, release date, and score from the result
    product_title = result.find_class('product_title')[0]
    name = product_title.text_content()
    link = 'http://metacritic.com' + product_title.find('a').attrib['href']

    try:
        release = result.find_class('release_date')[0].\
            find_class('data')[0].text_content()

        # strip extra spaces out of the release date
        release = re.sub(r'\s{2,}', ' ', release)
    except IndexError:
        release = None

    try:
        score = result.find_class('metascore')[0].text_content()
    except IndexError:
        score = None

    return '[%s] %s - %s, %s -- %s' % (plat.upper(), name,
            score or 'no score',
            'release: %s' % release if release else 'unreleased',
            link)
