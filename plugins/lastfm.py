from datetime import datetime

import requests
import random

from cloudbot import hook
from cloudbot.util import timeformat, web

api_url = "http://ws.audioscrobbler.com/2.0/?format=json"


@hook.command("lastfm", "nowplaying", "l", "last", "lfm", autohelp=False)
def lastfm(text, nick, db, bot, notice):
    """[user] [dontsave] - displays the now playing (or last played) track of LastFM user [user]"""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "Error: No last.fm API key has been set."

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

    params = {'method': 'user.getrecenttracks',
              'api_key': api_key, 'user': user, 'limit': 1}
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
        status = 'is listening to the song'
        ending = ''
    elif type(tracks) == dict:
        # otherwise, they aren't listening to anything right now, and
        # the tracks entry is a dict representing the most recent track
        track = tracks
        status = 'last listened to the song'
        # lets see how long ago they listened to it
        time_listened = datetime.fromtimestamp(int(track["date"]["uts"]))
        time_since = timeformat.time_since(time_listened)
        ending = ' ({} ago)'.format(time_since)

    else:
        return "Error: Could not parse track listing."

    title = track["name"]
    album = track["album"]["#text"]
    artist = track["artist"]["#text"]
    url = web.try_shorten(track["url"])

    out = '{} {} "{}"'.format(user, status, title)
    if artist:
        out += " by \x02{}\x0f".format(artist)
    if album:
        out += " from the album \x02{}\x0f -".format(album)
    if url:
        out += " {}".format(url)

    # append ending based on what type it was
    out += ending

    if text and not dontsave:
        db.execute("insert or replace into lastfm(nick, acc) values (:nick, :account)",
                   {'nick': nick.lower(), 'account': user})
        db.commit()

    return out


@hook.command("lastfmcompare", "compare", "lc")
def lastfmcompare(text, nick, bot, db):
    """[user] ([user] optional) - displays the now playing (or last played) track of LastFM user [user]"""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "Error: No last.fm API key has been set."
    if not text:
        return("Please specify a last.fm username to compare.")
    try:
        user1, user2 = text.split()
    except:
        user2 = text
        user1 = nick

    user2_check = db.execute(
        "select acc from lastfm where nick=lower(:nick)", {'nick': user2}).fetchone()
    if user2_check:
        user2 = user2_check[0]

    user1_check = db.execute(
        "select acc from lastfm where nick=lower(:nick)", {'nick': user1}).fetchone()
    if user1_check:
        user1 = user1_check[0]

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
    if 'error' in data:
        return "Error: {}.".format(data["message"])

    score = float(
        format(float(data["comparison"]["result"]["score"]) * 100, '.1f'))
    if score == 0:
        return "{} and {} have no common listening history.".format(user2, user1)
    level = "Super" if score > 95 else "Very High" if score > 80 else "High" if score > 60 else \
            "Medium" if score > 40 else "Low" if score > 10 else "Very Low"

    # I'm not even going to try to rewrite this line
    _artists = data["comparison"]["result"]["artists"]
    if type(_artists["artist"]) == list:
        artists = [f["name"] for f in _artists["artist"]]
    elif "artist" in _artists:
        artists = [_artists["artist"]["name"]]
    else:
        artists = ""

    return "Musical compatibility between \x02{}\x02 and \x02{}\x02: {} (\x02{}%\x02) {}".format(user1, user2, level,
                                                                                                 score, artist_string)


@hook.command("ltop", "ltt", "toptrack", autohelp=False)
def toptrack(text, nick, db, bot, notice):
    """-- Grabs a list of the top tracks for a last.fm username."""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "Error: No last.fm API key has been set."

    if text:
        username = db.execute(
            "select acc from lastfm where nick=lower(:nick)", {'nick': text}).fetchone()
        if not username:
            username = text
        else:
            username = username[0]
    else:
        username = db.execute("select acc from lastfm where nick=lower(:nick)",
                              {'nick': nick}).fetchone()
        username = username[0]
    if not username:
        return("No last.fm username specified and no last.fm username is set in the database.")

    params = {
        'api_key': api_key,
        'method': 'user.gettoptracks',
        'user': username,
        'limit': 10
    }
    request = requests.get(api_url, params=params)

    if request.status_code != requests.codes.ok:
        return "Failed to fetch info ({})".format(request.status_code)

    data = request.json()
    if 'error' in data:
        return "Error: {}.".format(data["message"])
    #response = http.get_json(api_url, api_key=api_key, method="user.gettoptracks", user=username)
    out = "{}'s favorite songs: ".format(username)
    for r in range(5):
        out = out + "{} by {} listened to {} times. ".format(data["toptracks"]["track"][r]["name"], data[
                                                             "toptracks"]["track"][r]["artist"]["name"], data["toptracks"]["track"][r]["playcount"])
    notice(out, nick)


@hook.command("lta", "topartist", autohelp=False)
def topartists(text, nick, db, bot, notice):
    """Grabs a list of the top artists for a last.fm username. You can set your lastfm username with .l username"""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "Error: No last.fm API key has been set."

    if text:
        username = db.execute(
            "select acc from lastfm where nick=lower(:nick)", {'nick': text}).fetchone()
        if not username:
            username = text
        else:
            username = username[0]
    else:
        username = db.execute("select acc from lastfm where nick=lower(:nick)",
                              {'nick': nick}).fetchone()
        username = username[0]
    if not username:
        return("No last.fm username specified and no last.fm username is set in the database.")
    params = {
        'api_key': api_key,
        'method': 'user.gettopartists',
        'user': username,
        'limit': 5
    }
    request = requests.get(api_url, params=params)

    if request.status_code != requests.codes.ok:
        return "Failed to fetch info ({})".format(request.status_code)

    data = request.json()
    if 'error' in data:
        return "Error: {}.".format(data["message"])

    #response = http.get_json(api_url, api_key=api_key, method="user.gettopartists", user=username, limit=5 )
    out = "{}'s favorite artists: ".format(username)
    for r in range(5):
        out = out + "{} listened to {} times. ".format(
            data["topartists"]["artist"][r]["name"], data["topartists"]["artist"][r]["playcount"])
    notice(out, nick)


@hook.command("lt", "ltrack", autohelp=False)
def lastfm_track(text, nick, db, bot, notice):
    """Grabs a list of the top tracks for a last.fm username"""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "Error: No last.fm API key has been set."
    artist = ""
    track = ""
    if text:
        params = text.split(',')
        if len(params) < 2:
            notice(
                "Please specify an artist and track title in the form artist name, track name.", nick)
            return
        else:
            artist = params[0]
            track = params[1]
    else:
        notice(
            "Please specify an artist and track title in the form artist name, track name.", nick)
        return
    username = db.execute("select acc from lastfm where nick=lower(:nick)",
                          {'nick': nick}).fetchone()
    if username:
        username = username[0]
        params = {
            'api_key': api_key,
            'method': 'track.getInfo',
            'artist': artist,
            'track': track,
            'username': username,
            'autocorrect': 1
        }
    else:
        params = {
            'api_key': api_key,
            'method': 'track.getInfo',
            'artist': artist,
            'track': track,
            'autocorrect': 1
        }
        #response = http.get_json(api_url, api_key=api_key, method="track.getInfo", artist=artist, track=track, autocorrect=1)
    request = requests.get(api_url, params=params)

    if request.status_code != requests.codes.ok:
        return "Failed to fetch info ({})".format(request.status_code)

    response = request.json()
    if 'error' in response:
        return "Error: {}.".format(response["message"])

    track_name = response["track"]["name"]
    artist_name = response["track"]["artist"]["name"]
    album_name = response["track"]["album"]["title"]
    url = web.try_shorten(response["track"]["url"])
    listeners = response["track"]["listeners"]
    playcount = response["track"]["playcount"]
    out = out = "'{}' from the album {} by {} has been played {} times by {} listeners. {}".format(
        track_name, album_name, artist_name, playcount, listeners, url)
    if 'userplaycount' in response["track"]:
        userplaycount = response["track"]["userplaycount"]
        out = "'{}' from the album {} by {} has been played {} times by {} listeners. {} has listened {} times. {}".format(
            track_name, album_name, artist_name, playcount, listeners, username, userplaycount, url)
    return out


@hook.command("la", "lartist", autohelp=False)
def lastfm_artist(text, nick, db, bot, notice):
    """<artist> prints information about the specified artist"""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "Error: No last.fm API key has been set."
    artist = text
    params = ""
    if text:
        pass
    else:
        notice("Please specify an artist.", nick)
    username = db.execute("select acc from lastfm where nick=lower(:nick)",
                          {'nick': nick}).fetchone()
    if username:
        username = username[0]
        params = {
            'api_key': api_key,
            'method': 'artist.getInfo',
            'artist': artist,
            'username': username,
            'autocorrect': 1
        }
    else:
        params = {
            'api_key': api_key,
            'method': 'artist.getInfo',
            'artist': artist,
            'autocorrect': 1
        }

    request = requests.get(api_url, params=params)

    if request.status_code != requests.codes.ok:
        return "Failed to fetch info ({})".format(request.status_code)

    response = request.json()
    if 'error' in response:
        return "Error: {}.".format(response["message"])
    artist_name = response["artist"]["name"]
    url = web.try_shorten(response["artist"]["url"])
    listeners = response["artist"]["stats"]["listeners"]
    playcount = response["artist"]["stats"]["playcount"]
    out = out = "{} has been played {} times by {} listeners. {}".format(
        artist_name, playcount, listeners, url)
    if 'userplaycount' in response["artist"]["stats"]:
        userplaycount = response["artist"]["stats"]["userplaycount"]
        out = "'{}' has been played {} times by {} listeners. {} has listened {} times. {}".format(
            artist_name, playcount, listeners, username, userplaycount, url)
    return out
