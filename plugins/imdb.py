# IMDb lookup plugin by Ghetto Wizard (2011) and blha303 (2013)

from util import hook, http
import re
import json

id_re = re.compile("tt\d+")

def truncate(msg):
    nmsg = msg.split(" ")
    out = None
    x = 0
    for i in nmsg:
      if x <= 7:
        if out:
          out = out + " " + nmsg[x]
        else:
          out = nmsg[x]
      x = x + 1
    if x <= 7:
      return out
    else:
      return out + "..."

@hook.command
def imdb(inp):
    "imdb <movie> -- Gets information about <movie> from IMDb."

    strip = inp.strip()

    if id_re.match(strip):
        content = http.get_json("http://www.omdbapi.com/", i=strip)
    else:
        content = http.get_json("http://www.omdbapi.com/", t=strip)

    if content.get('Error', None) == 'Movie not found!':
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

imdb_re = (r'(.*:)//(imdb.com|www.imdb.com)(:[0-9]+)?(.*)', re.I)

@hook.regex(*imdb_re)
def imdb_url(match):
    id = match.group(4).split('/')[-1]
    if id == "":
      id = match.group(4).split('/')[-2]
    content = http.get_json("http://www.omdbapi.com/", i=id)
    if content.get('Error', None) == 'Movie not found!':
        return 'Movie not found!'
    elif content['Response'] == 'True':
        content['URL'] = 'http://www.imdb.com/title/%(imdbID)s' % content
        content['Plot'] = truncate(content['Plot'])
        out = '\x02%(Title)s\x02 (%(Year)s) (%(Genre)s): %(Plot)s'
        if content['Runtime'] != 'N/A':
            out += ' \x02%(Runtime)s\x02.'
        if content['imdbRating'] != 'N/A' and content['imdbVotes'] != 'N/A':
            out += ' \x02%(imdbRating)s/10\x02 with \x02%(imdbVotes)s\x02' \
                   ' votes.'
        return out % content
    else:
        return 'Unknown error.'
