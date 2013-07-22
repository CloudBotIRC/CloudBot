from util import hook, http, web, text
from urllib import urlencode
import re

sc_re = (r'(.*:)//(www.)?(soundcloud.com)(.*)', re.I)
api_url = "http://api.soundcloud.com"


@hook.regex(*sc_re)
def soundcloud_url(match, bot=None):
    api_key = bot.config.get("api_keys", {}).get("soundcloud")
    if not api_key:
        return "error: no api key set"

    url = match.group(1).split(' ')[-1] + "//" + (match.group(2) if match.group(2) else "") + match.group(3) + match.group(4).split(' ')[0]
    data = http.get_json(api_url + '/resolve.json?' + urlencode({'url': url, 'client_id': api_key}))

    if data['description']:
        desc = u": {} ".format(text.truncate_str(data['description'], 50))
    else:
        desc = ""
    if data['genre']:
        genre = u"- Genre: \x02{}\x02 ".format(data['genre'])
    else:
        genre = ""

    try:
        url = web.isgd(data['permalink_url'])
    except (web.ShortenError, http.HTTPError):
        url = data['permalink_url']

    return u"SoundCloud track: \x02{}\x02 by \x02{}user\x02 {}{}- {} plays, {} downloads, {} comments - \x02{}\x02".format(data['title'], data['user']['username'], desc, genre, data['playback_count'], data['download_count'], data['comment_count'], url)