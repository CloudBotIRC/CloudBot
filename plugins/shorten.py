# # Lukeroge
from util import hook, http

try:
  from re import match
  from urllib2 import urlopen, Request, HTTPError
  from urllib import urlencode
  
except ImportError, e:
  raise Exception('Required module missing: %s' % e.args[0])

class ShortenError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
 
def tiny(url, user, apikey):
  try:
    params = urlencode({'longUrl': url, 'login': user, 'apiKey': apikey, 'format': 'json'})
    j = http.get_json("http://api.bit.ly/v3/shorten?%s" % params)
    if j['status_code'] == 200:
      return j['data']['url']
    raise ShortenError('%s'%j['status_txt'])
  except (HTTPError, ShortenError):
    return "Could not shorten %s!" % url

@hook.command
def shorten(inp, bot = None):
  ".shorten <url> - Makes an j.mp/bit.ly shortlink to the url provided"
  user = bot.config['api_keys']['bitly_user']
  api = bot.config['api_keys']['bitly_api']
  return tiny(inp, user, api)
