from datetime import datetime

import requests
import random

from cloudbot import hook
from cloudbot.util import timeformat

api_url = "http://ws.audioscrobbler.com/2.0/?format=json"


@hook.command("lastfm", "lfm", "l", autohelp=False)
def lastfm(text, nick, db, bot, notice):
    """[user] [dontsave] - displays the now playing (or last played) track of LastFM user [user]"""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "No last.fm API key set."

    # check if the user asked us not to save his details
    dontsave = text.endswith(" dontsave")
    if dontsave:
        user = text[:-9].strip().lower()
    else:
        user = text

    db.execute("create table if not exists lastfm(nick primary key, acc)")

    if not user:
        user = db.execute("select acc from lastfm where nick=lower(:nick)",
                          {'nick': nick}).fetchone()
        if not user:
            notice(lastfm.__doc__)
            return
        user = user[0]

    params = {'method': 'user.getrecenttracks', 'api_key': api_key, 'user': user, 'limit': 1}
    request = requests.get(api_url, params=params)

    if request.status_code != requests.codes.ok:
        return "Failed to fetch info ({})".format(request.status_code)

    response = request.json()

    if 'error' in response:
        return "Last.FM Error: {}.".format(response["message"])

    if "track" not in response["recenttracks"] or len(response["recenttracks"]["track"]) == 0:
        return 'No recent tracks for user "{}" found.'.format(user)

    tracks = response["recenttracks"]["track"]

    if type(tracks) == list:
        # if the user is listening to something, the tracks entry is a list
        # the first item is the current track
        track = tracks[0]
        status = 'is listening to'
        ending = '.'
    elif type(tracks) == dict:
        # otherwise, they aren't listening to anything right now, and
        # the tracks entry is a dict representing the most recent track
        track = tracks
        status = 'last listened to'
        # lets see how long ago they listened to it
        time_listened = datetime.fromtimestamp(int(track["date"]["uts"]))
        time_since = timeformat.time_since(time_listened)
        ending = ' ({} ago)'.format(time_since)

    else:
        return "error: could not parse track listing"

    title = track["name"]
    album = track["album"]["#text"]
    artist = track["artist"]["#text"]

    out = '{} {} "{}"'.format(user, status, title)
    if artist:
        out += " by \x02{}\x0f".format(artist)
    if album:
        out += " from the album \x02{}\x0f".format(album)

    # append ending based on what type it was
    out += ending

    if text and not dontsave:
        db.execute("insert or replace into lastfm(nick, acc) values (:nick, :account)",
                   {'nick': nick.lower(), 'account': user})
        db.commit()

    return out


@hook.command("lastfmcompare", "compare")
def lastfmcompare(text, bot):
    """[user] [dontsave] - displays the now playing (or last played) track of LastFM user [user]"""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "No last.fm API key set."

    user1, user2 = text.split()

    params = {
        'method': 'tasteometer.compare',
        'api_key': api_key,
        'type1': 'user',
        'value1': user1,
        'type2': 'user',
        'value2': user2
    }
    request = requests.get(api_url, params=params)

    if request.status_code != requests.codes.ok:
        return "Failed to fetch info ({})".format(request.status_code)

    data = request.json()

    score = int(float(data["comparison"]["result"]["score"]) * 100)
    level = "Super" if score > 95 else "Very High" if score > 80 else "High" if score > 60 else \
            "Medium" if score > 40 else "Low" if score > 10 else "Very Low"

    # I'm not even going to try to rewrite this line
    artists = [f["name"] for f in data["comparison"]["result"]["artists"]["artist"]] if \
        type(data["comparison"]["result"]["artists"]["artist"]) == list else \
        [data["comparison"]["result"]["artists"]["artist"]["name"]] if "artist" \
        in data["comparison"]["result"]["artists"] else ""
    artist_string = "\x02In Common:\x02 " + ", ".join(artists) if artists else ""

    return "Musical compatibility between \x02{}\x02 and \x02{}\x02: {} (\x02{}%\x02)".format(user1, user2, level,
                                                                                              score), artist_string
