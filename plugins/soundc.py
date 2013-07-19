from util import hook, http, web
import soundcloud
import re

sc_re = (r'(.*:)//(www.)?(soundcloud.com)(.*)', re.I)

@hook.regex(*sc_re)
def soundcloud_url(match, bot=None):
  api_key = bot.config.get("api_keys", {}).get("soundcloud")
  if not api_key:
    return "Error: no api key set"
  url = match.group(1).split(' ')[-1] + "//" + (match.group(2) if match.group(2) else "") + match.group(3) + match.group(4).split(' ')[0]
  client = soundcloud.Client(client_id=api_key)
  track = client.get('/resolve', url=url)
  try:
    return "SoundCloud track: \x02%s\x02 by \x02%s\x02 - \x02%s\x02" % (track.title, track.user['username'], web.isgd(track.permalink_url))
  except:
    return "SoundCloud user: \x02%s\x02 - \x02%s\x02" % (track.username, web.isgd(track.permalink_url))
