# # Lukeroge
from util import hook, http

try:
  from re import match
  from urllib2 import urlopen, Request, HTTPError
  from urllib import urlencode
  
except ImportError, e:
  raise Exception('Required module missing: %s' % e.args[0])
 
def tiny(url, user, apikey):
  try:
    params = urlencode({'longUrl': url, 'login': user, 'apiKey': apikey, 'format': 'json'})
    req = Request("http://api.bit.ly/v3/shorten?%s" % params)
    response = urlopen(req)
    j = http.get_json(response.read())
    if j['status_code'] == 200:
      return j['data']['url']
    raise Exception('%s'%j['status_txt'])
  except HTTPError, e:
    return "Invalid URL!"

@hook.command
def shorten(inp, bot = None):
  ".shorten <url> - Makes an j.mp/bit.ly shortlink to the url provided"
  user = bot.config['api_keys']['bitly_user']
  api = bot.config['api_keys']['bitly_api']
  return tiny(inp, user, api)
