# IMDb lookup plugin by Ghetto Wizard (2011).

from util import hook, http


@hook.command
def imdb(inp):
    '''.imdb <movie> -- gets information about <movie> from IMDb'''

    content = http.get_json("http://www.imdbapi.com/", t=inp)

    if content['Response'] == 'Movie Not Found':
        return 'movie not found'
    elif content['Response'] == 'True':
        content['URL'] = 'http://www.imdb.com/title/%(ID)s' % content

        out = '\x02%(Title)s\x02 (%(Year)s) (%(Genre)s): %(Plot)s'
        if content['Runtime'] != 'N/A':
            out += ' \x02%(Runtime)s\x02.'
        if content['Rating'] != 'N/A' and content['Votes'] != 'N/A':
            out += ' \x02%(Rating)s/10\x02 with \x02%(Votes)s\x02 votes.'
        out += ' %(URL)s'
        return out % content
    else:
        return 'unknown error'
