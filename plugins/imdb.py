# IMDb lookup plugin by Ghetto Wizard (2011).

from util import hook, http
import re

id_re = re.compile("tt\d+")


@hook.command
def imdb(inp):
    "imdb <movie> -- Gets information about <movie> from IMDb."

    strip = inp.strip()

    if id_re.match(strip):
        content = http.get_json("http://www.omdbapi.com/", i=strip)
    else:
        content = http.get_json("http://www.omdbapi.com/", t=strip)

    if content['Error'] == 'Movie not found!':
        return 'Movie not found!'
    elif content['Response'] == 'True':
        content['URL'] = 'http://www.imdb.com/title/%(imdbID)s' % content

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
