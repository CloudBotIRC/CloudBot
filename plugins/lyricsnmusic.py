import requests

from cloudbot import hook
from cloudbot.util import web
#
api_url = "http://api.lyricsnmusic.com/songs"

@hook.command("lyrics")
def lyricsnmusic(text,bot):
    """lyrics <artist and/or song> will fetch the first 150 characters of a song and a link to the full lyrics."""
    api_key = bot.config.get("api_keys", {}).get("lyricsnmusic")
    params = { "api_key": api_key, "q": text}
    r = requests.get(api_url, params=params)
    if r.status_code != 200:
        return "There was an error returned by the LyricsNMusic API."
    r = r.json()
    snippet = r[0]["snippet"].replace("\r\n"," ")
    url = web.try_shorten(r[0]["url"])
    title = r[0]["title"]
    viewable = r[0]["viewable"]        
    out = "\x02{}\x02 -- {} {}".format(title, snippet, url)
    if not viewable:
        out += " Full lyrics not available."
    return out
