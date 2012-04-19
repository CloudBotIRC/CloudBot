# Upgraded with tables/caching by ChauffeR of #freebnc on irc.esper.net
from util import hook, http


@hook.command('l', autohelp=False)
@hook.command(autohelp=False)
def lastfm(inp, nick='', say=None, db=None, bot=None):
    ".lastfm [user] -- Displays the now playing (or last played) " \
    "track of LastFM user [user]."
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    if inp:
        user = inp
    else:
        user = nick
    db.execute("create table if not exists lastfm(nick primary key, acc)")
    sql = db.execute("select acc from lastfm where nick=lower(?)", (nick,)).fetchone();
    api_url = "http://ws.audioscrobbler.com/2.0/?format=json"


    if sql:
        if not inp: user = sql[0]
        else:
            user = inp
            db.execute("insert or replace into lastfm(nick,acc) values(?,?)", (nick.lower(), user))
            db.commit()
    else:
        if not inp: user = nick
        else:
            user = inp
            db.execute("insert or replace into lastfm(nick,acc) values(?,?)", (nick.lower(), user))
            db.commit()

    response = http.get_json(api_url, method="user.getrecenttracks",
                             api_key=api_key, user=user, limit=1)

    if 'error' in response:
        if inp:  # specified a user name
            return "error: %s" % response["message"]
        else:
            return "Your nick is not a LastFM account. Try '.lastfm [user]'"

    if not "track" in response["recenttracks"] or len(response["recenttracks"]["track"]) == 0:
        return "No recent tracks for user \x02%s\x0F found" % user
		
    tracks = response["recenttracks"]["track"]

    if type(tracks) == list:
        # if the user is listening to something, the tracks entry is a list
        # the first item is the current track
        track = tracks[0]
        status = 'current track'
    elif type(tracks) == dict:
        # otherwise, they aren't listening to anything right now, and
        # the tracks entry is a dict representing the most recent track
        track = tracks
        status = 'last track'
    else:
        return "error: could not parse track listing"

    title = track["name"]
    album = track["album"]["#text"]
    artist = track["artist"]["#text"]

    out = "\x02%s\x0F's %s - \x02%s\x0f" % (user, status, title)
    if artist:
        out += ' by "\x02%s\x0f"' % artist
    if album:
        out += ' from the album "\x02%s\x0f"' % album

    return out
