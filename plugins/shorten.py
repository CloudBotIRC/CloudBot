# # Lukeroge
from util import hook

try:
  from re import match
  from urllib2 import urlopen, Request, HTTPError
  from urllib import urlencode
  from simplejson import loads
except ImportError, e:
  raise Exception('Required module missing: %s' % e.args[0])
 
user = "o_750ro241n9"
apikey  = "R_f3d0a9b478c53d247a134d0791f898fe"
 
def expand(url):
  try:
    params = urlencode({'shortUrl': url, 'login': user, 'apiKey': apikey, 'format': 'json'})
    req = Request("http://api.bit.ly/v3/expand?%s" % params)
    response = urlopen(req)
    j = loads(response.read())
    if j['status_code'] == 200:
      return j['data']['expand'][0]['long_url']
    raise Exception('%s'%j['status_txt'])
  except HTTPError, e:
    raise('HTTP Error%s'%e.read())
 
def tiny(url):
  try:
    params = urlencode({'longUrl': url, 'login': user, 'apiKey': apikey, 'format': 'json'})
    req = Request("http://api.bit.ly/v3/shorten?%s" % params)
    response = urlopen(req)
    j = loads(response.read())
    if j['status_code'] == 200:
      return j['data']['url']
    raise Exception('%s'%j['status_txt'])
  except HTTPError, e:
    raise('HTTP error%s'%e.read())

@hook.command
def shorten(inp):
  ".shorten <url> - Makes an j.mp shortlink to the url provided"
  return tiny(inp)
