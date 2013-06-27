#!/usr/bin/env python
from util import hook
import oauth2 as oauth
import urllib, json

CONSUMER_KEY = "jk53y8a3fj93jf2wq78amemk"
CONSUMER_SECRET = "BbEeBbQYFA"

def getdata(inp, types):
  consumer = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
  client = oauth.Client(consumer)
  response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode({'method': 'search', 'query': inp, 'types': types, 'count': '1'}))
  data = json.loads(response[1])
  return data

@hook.command
def rdio(inp):
  """ rdio <search term> - alternatives: .rdiot (track), .rdioar (artist), .rdioal (album) """
  data = getdata(inp, "Track,Album,Artist")
  try:
    info = data['result']['results'][0]
  except IndexError:
    return "No results."
  if 'name' in info:
    if 'artist' in info and 'album' in info: #Track
      name = info['name']
      artist = info['artist']
      album = info['album']
      url = info['shortUrl']
      return u"\x02{}\x02 by \x02{}\x02 - {} {}".format(name, artist, album, url)
    elif 'artist' in info and not 'album' in info: #Album
      name = info['name']
      artist = info['artist']
      url = info['shortUrl']
      return u"\x02{}\x02 by \x02{}\x02 - {}".format(name, artist, url)
    else: #Artist
      name = info['name']
      url = info['shortUrl']
      return u"\x02{}\x02 {}".format(name, url)

@hook.command
def rdiot(inp):
  """ rdiot <search term> - Search for tracks on rdio """
  data = getdata(inp, "Track")
  try:
    info = data['result']['results'][0]
  except IndexError:
    return "No results."
  name = info['name']
  artist = info['artist']
  album = info['album']
  url = info['shortUrl']
  return u"\x02{}\x02 by \x02{}\x02 - {} {}".format(name, artist, album, url)

@hook.command
def rdioar(inp):
  """ rdioar <search term> - Search for artists on rdio """
  data = getdata(inp, "Artist")
  try:
    info = data['result']['results'][0]
  except IndexError:
    return "No results."
  name = info['name']
  url = info['shortUrl']
  return u"\x02{}\x02 {}".format(name, url)

@hook.command
def rdioal(inp):
  """ rdioal <search term> - Search for albums on rdio """
  data = getdata(inp, "Album")
  try:
    info = data['result']['results'][0]
  except IndexError:
    return "No results."
  name = info['name']
  artist = info['artist']
  url = info['shortUrl']
  return u"\x02{}\x02 by \x02{}\x02 - {}".format(name, artist, url)

import re
import urllib2

rdio_re = (r'(.*:)//(rd.io|www.rdio.com|rdio.com)(:[0-9]+)?(.*)', re.I)

@hook.regex(*rdio_re)
def rdio_url(match):
    url = match.group(1) + "//" + match.group(2) + match.group(4)
    consumer = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    client = oauth.Client(consumer)
    response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode({'method': 'getObjectFromUrl', 'url': url}))
    data = json.loads(response[1])
    info = data['result']
    if 'name' in info:
      if 'artist' in info and 'album' in info: #Track
        name = info['name']
        artist = info['artist']
        album = info['album']
        return u"Rdio track: \x02{}\x02 by \x02{}\x02 - {}".format(name, artist, album)
      elif 'artist' in info and not 'album' in info: #Album
        name = info['name']
        artist = info['artist']
        return u"Rdio album: \x02{}\x02 by \x02{}\x02".format(name, artist)
      else: #Artist
        name = info['name']
        return u"Rdio artist: \x02{}\x02".format(name)
