import re
from util import hook, http

twitch_re = (r'(.*:)//(twitch.tv|www.twitch.tv)(:[0-9]+)?(.*)', re.I)
valid = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_/')

def test(s):
   return set(s) <= valid

@hook.regex(*twitch_re)
def twitch_url(match):
    location = "/".join(match.group(4).split("/")[1:])
    if not test(match.group(4).split("/")[1]):
      return "Not a valid username"
    soup = http.get_soup("http://twitch.tv/" + location)
    try:
      title = soup.findAll('span', {'class': 'real_title js-title'})[0].text
    except IndexError:
      return "That user has no stream or videos."
    online = True
    try:
      isplaying = soup.findAll('a', {'data-content_type': 'live'})[0];
    except IndexError:
      online = False
    try:
      name = soup.findAll('a', {'class': 'channel_name'})[0].text
    except IndexError:
      name = soup.findAll('a', {'class': 'channelname'})[0].text
    playing = soup.findAll('a', {'class': 'game js-game'})[0].text
    if playing == "/directory/game/":
      np = False
    else:
      np = True
    if online:
      if np:
        return u"%s: %s playing %s (\x033\x02Online now!\x02\x0f)" % (title, name, playing)
      else:
        return u"%s: %s (\x033\x02Online now!\x02\x0f)" % (title, name)
    else:
      if np:
        return u"%s: %s playing %s (\x034\x02Offline\x02\x0f)" % (title, name, playing)
      else:
        return u"%s: %s (\x034\x02Offline\x02\x0f)" % (title, name)
