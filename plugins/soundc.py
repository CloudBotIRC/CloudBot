from util import hook, http, web
from urllib import urlencode
import re

sc_re = (r'(.*:)//(www.)?(soundcloud.com)(.*)', re.I)

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

@hook.regex(*sc_re)
def soundcloud_url(match, bot=None):
  api_key = bot.config.get("api_keys", {}).get("soundcloud")
  if not api_key:
    return "Error: no api key set"
  url = match.group(1).split(' ')[-1] + "//" + (match.group(2) if match.group(2) else "") + match.group(3) + match.group(4).split(' ')[0]
  apiurl = "http://api.soundcloud.com"
  track = http.get_json(apiurl + '/resolve.json?' + urlencode({'url': url, 'client_id': api_key}))
  if track['description']:
    desc = ": %s " % truncate(track['description'])
  else:
    desc = ""
  if track['genre'] != "":
    genre = "- Genre: \x02%s\x02 " % track['genre']
  else:
    genre = ""
  return "SoundCloud track: \x02%s\x02 by \x02%s\x02 %s%s- %s plays, %s downloads, %s comments - \x02%s\x02" % (track['title'], track['user']['username'], desc, genre, track['playback_count'], track['download_count'], track['comment_count'], web.isgd(track['permalink_url']))
