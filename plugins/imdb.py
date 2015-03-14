import re

import requests

from cloudbot import hook


id_re = re.compile("tt\d+")
imdb_re = re.compile(r'(.*:)//(imdb.com|www.imdb.com)(:[0-9]+)?(.*)', re.I)


@hook.command
def imdb(text, bot):
    """imdb <movie> - gets information about <movie> from IMDb"""

    headers = {'User-Agent': bot.user_agent}
    strip = text.strip()

    if id_re.match(strip):
        params = {'i': strip}
    else:
        params = {'t': strip}

    request = requests.get("http://www.omdbapi.com/", params=params, headers=headers)
    content = request.json()

    if content.get('Error', None) == 'Movie not found!':
        return 'Movie not found!'
    elif content['Response'] == 'True':
        content['URL'] = 'http://www.imdb.com/title/{}'.format(content['imdbID'])

        out = '\x02%(Title)s\x02 (%(Year)s) (%(Genre)s): %(Plot)s'
        if content['Runtime'] != 'N/A':
            out += ' \x02%(Runtime)s\x02.'
        if content['imdbRating'] != 'N/A' and content['imdbVotes'] != 'N/A':
            out += ' \x02%(imdbRating)s/10\x02 with \x02%(imdbVotes)s\x02' \
                   ' votes.'
        out += ' %(URL)s'
        return out % content
    else:
        return 'Unknown error.'


@hook.regex(imdb_re)
def imdb_url(match, bot):
    headers = {'User-Agent': bot.user_agent}

    imdb_id = match.group(4).split('/')[-1]
    if imdb_id == "":
        imdb_id = match.group(4).split('/')[-2]

    params = {'i': imdb_id}
    request = requests.get("http://www.omdbapi.com/", params=params, headers=headers)
    content = request.json()

    if content['Response'] == 'True':
        out = '\x02%(Title)s\x02 (%(Year)s) (%(Genre)s): %(Plot)s'
        if content['Runtime'] != 'N/A':
            out += ' \x02%(Runtime)s\x02.'
        if content['imdbRating'] != 'N/A' and content['imdbVotes'] != 'N/A':
            out += ' \x02%(imdbRating)s/10\x02 with \x02%(imdbVotes)s\x02' \
                   ' votes.'
        return out % content
