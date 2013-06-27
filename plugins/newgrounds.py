import re
from util import hook, http
import json
from BeautifulSoup import BeautifulSoup
import urllib2

newgrounds_re = (r'(.*:)//(www.newgrounds.com|newgrounds.com)(:[0-9]+)?(.*)', re.I)
valid = set('0123456789')

def test(s):
   return set(s) <= valid

@hook.regex(*newgrounds_re)
def newgrounds_url(match):
    location = match.group(4).split("/")[-1]
    if not test(location):
      return "Not a valid Newgrounds portal ID. Example: http://www.newgrounds.com/portal/view/593993"
    try:
      urlobj = urllib2.urlopen("http://www.newgrounds.com/portal/view/" + location)
    except urllib2.HTTPError:
      return "\x034\x02Invalid response. Maybe Newgrounds is down for maintenance?"
    soup = BeautifulSoup(urlobj.read())
    try:
      title = soup.find('title').text
      author = soup.find('ul', {'class': 'authorlinks'}).find('img')['alt']
      rating = u"\x02%s\x02/\x025.0\x02" % soup.find('dd', {'class': 'star-variable'})['title'].split("Stars &ndash;")[0].strip()
      numofratings = soup.find('dd', {'class': 'star-variable'})['title'].split("Stars &ndash;")[1].replace("Votes", "").strip()
      views = soup.find('dl', {'class': 'contentdata'}).findAll('dd')[1].find('strong').text
      date = soup.find('dl', {'class': 'sidestats'}).find('dd').text
    except Exception:
      return "\x034\x02Could not find item information."
    return u"\x02%s\x02 - rated %s (%s) - \x02%s\x02 views - \x02%s\x02 on \x02%s\x02" % (title, rating, numofratings, views, author, date)
