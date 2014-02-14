# IMDb lookup plugin by Ghetto Wizard (2011) and blha303 (2013)

import re

from util import hook, http, text


id_re = re.compile("tt\d+")
imdb_re = (r'(.*:)//(imdb.com|www.imdb.com)(:[0-9]+)?(.*)', re.I)


@hook.command
def imdb(inp):
    """imdb <movie> -- Gets information about <movie> from IMDb."""

    strip = inp.strip()

    if id_re.match(strip):
        content = http.get_json("http://www.omdbapi.com/", i=strip)
    else:
        content = http.get_json("http://www.omdbapi.com/", t=strip)

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


@hook.regex(*imdb_re)
def imdb_url(match):
    imdb_id = match.group(4).split('/')[-1]
    if imdb_id == "":
        imdb_id = match.group(4).split('/')[-2]
    content = http.get_json("http://www.omdbapi.com/", i=imdb_id)
    if content.get('Error', None) == 'Movie not found!':
        return 'Movie not found!'
    elif content['Response'] == 'True':
        content['URL'] = 'http://www.imdb.com/title/%(imdbID)s' % content
        content['Plot'] = text.truncate_str(content['Plot'], 50)
        out = '\x02%(Title)s\x02 (%(Year)s) (%(Genre)s): %(Plot)s'
        if content['Runtime'] != 'N/A':
            out += ' \x02%(Runtime)s\x02.'
        if content['imdbRating'] != 'N/A' and content['imdbVotes'] != 'N/A':
            out += ' \x02%(imdbRating)s/10\x02 with \x02%(imdbVotes)s\x02' \
                   ' votes.'
        return out % content
    else:
        return 'Unknown error.'
