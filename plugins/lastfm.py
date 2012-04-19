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
	
    api_url = "http://ws.audioscrobbler.com/2.0/?format=json"

    dontsave = user.endswith(" dontsave")
    if dontsave:
        user = user[:-9].strip().lower()

    db.execute("create table if not exists lastfm(nick primary key, acc)")

    if not user:
        user = db.execute("select acc from lastfm where nick=lower(?)",
                          (nick,)).fetchone()
        if not user:
            notice(lastfm.__doc__)
            return
        user = user[0]

    response = http.get_json(api_url, method="user.getrecenttracks",
                             api_key=api_key, user=user, limit=1)

    if 'error' in response:
        if inp:  # specified a user name
            return "Error: %s." % response["message"]
        else:
            return "Your nick is not a LastFM account. Try '.lastfm [user]'"

    if not "track" in response["recenttracks"] or len(response["recenttracks"]["track"]) == 0:
        return 'No recent tracks for user "%s" found.' % user
		
    tracks = response["recenttracks"]["track"]

    if type(tracks) == list:
        # if the user is listening to something, the tracks entry is a list
        # the first item is the current track
        track = tracks[0]
        status = 'is listening to'
    elif type(tracks) == dict:
        # otherwise, they aren't listening to anything right now, and
        # the tracks entry is a dict representing the most recent track
        track = tracks
        status = 'last listened to'
    else:
        return "error: could not parse track listing"

    title = track["name"]
    album = track["album"]["#text"]
    artist = track["artist"]["#text"]

    out = "%s %s \x02%s\x0f" % (user, status, title)
    if artist:
        out += ' by "\x02%s\x0f"' % artist
    if album:
        out += ' from the album "\x02%s\x0f"' % album
		
    if inp and not dontsave:
        db.execute("insert or replace into lastfm(nick, acc) values (?,?)",
                     (nick.lower(), user))
        db.commit()

    return out
