from datetime import datetime

import requests

from sqlalchemy import Table, Column, PrimaryKeyConstraint, String

from cloudbot import hook
from cloudbot.util import timeformat, web, database

api_url = "http://ws.audioscrobbler.com/2.0/?format=json"

table = Table(
    "lastfm",
    database.metadata,
    Column('nick', String(25)),
    Column('acc', String(25)),
    PrimaryKeyConstraint('nick')
)


@hook.on_start()
def load_cache(db):
    """
    :type db: sqlalchemy.orm.Session
    """
    global last_cache
    last_cache = []
    for row in db.execute(table.select()):
        nick = row["nick"]
        account = row["acc"]
        last_cache.append((nick, account))


def get_account(nick):
    """looks in last_cache for the lastfm account name"""
    last_account = [row[1] for row in last_cache if nick.lower() == row[0]]
    if not last_account:
        return
    else:
        last_account = last_account[0]
    return last_account


@hook.command("lastfm", "last", "np", "l", autohelp=False)
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

    if not user:
        user = get_account(nick)
        if not user:
            notice(lastfm.__doc__)
            return

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
    url = web.try_shorten(track["url"])

    out = '{} {} "{}"'.format(user, status, title)
    if artist:
        out += " by \x02{}\x0f".format(artist)
    if album:
        out += " from the album \x02{}\x0f".format(album)
    if url:
        out += " {}".format(url)

    # append ending based on what type it was
    out += ending

    if text and not dontsave:
        db.execute("insert or replace into lastfm(nick, acc) values (:nick, :account)",
                   {'nick': nick.lower(), 'account': user})
        db.commit()
        load_cache(db)
    return out


@hook.command("lastfmcompare", "compare", "lc")
def lastfmcompare(text, nick, bot,):
    """[user] ([user] optional) - displays the now playing (or last played) track of LastFM user [user]"""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "No last.fm API key set."
    if not text:
        return "please specify a lastfm username to compare"
    try:
        user1, user2 = text.split()
    except:
        user2 = text
        user1 = nick

    user2_check = get_account(user2)
    if user2_check:
        user2 = user2_check

    user1_check = get_account(user1)
    if user1_check:
        user1 = user1_check

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

    score = float(data["comparison"]["result"]["score"])
    score = float("{:.3f}".format(score * 100))
    if score == 0:
        return "{} and {} have no common listening history.".format(user2, user1)
    level = "Super" if score > 95 else "Very High" if score > 80 else "High" if score > 60 else \
            "Medium" if score > 40 else "Low" if score > 10 else "Very Low"

    # I'm not even going to try to rewrite this line
    artists = [f["name"] for f in data["comparison"]["result"]["artists"]["artist"]] if \
        type(data["comparison"]["result"]["artists"]["artist"]) == list else \
        [data["comparison"]["result"]["artists"]["artist"]["name"]] if "artist" \
        in data["comparison"]["result"]["artists"] else ""
    artist_string = "\x02In Common:\x02 " + \
        ", ".join(artists) if artists else ""

    return "Musical compatibility between \x02{}\x02 and \x02{}\x02: {} (\x02{}%\x02) {}".format(user1, user2, level,
                                                                                                 score, artist_string)


@hook.command("ltop", "ltt", autohelp=False)
def toptrack(text, nick, bot):
    """Grabs a list of the top tracks for a last.fm username"""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    if text:
        username = get_account(text)
        if not username:
            username = text
    else:
        username = get_account(nick)
    if not username:
        return "No last.fm username specified and no last.fm username is set in the database."

    params = {
        'api_key': api_key,
        'method': 'user.gettoptracks',
        'user': username,
        'limit': 5
    }
    request = requests.get(api_url, params=params)

    if request.status_code != requests.codes.ok:
        return "Failed to fetch info ({})".format(request.status_code)

    data = request.json()
    if 'error' in data:
        return "Error: {}.".format(data["message"])
    out = "{}'s favorite songs: ".format(username)
    for r in range(5):
        track_name = data["toptracks"]["track"][r]["name"]
        artist_name = data["toptracks"]["track"][r]["artist"]["name"]
        play_count = data["toptracks"]["track"][r]["playcount"] 
        out = out + "{} by {} listened to {} times. ".format(track_name, artist_name, play_count)
    return out


@hook.command("lta", "topartist", autohelp=False)
def topartists(text, nick, bot):
    """Grabs a list of the top artists for a last.fm username. You can set your lastfm username with .l username"""
    api_key = bot.config.get("api_keys", {}).get("lastfm")
    if not api_key:
        return "error: no api key set"

    if text:
        username = get_account(text)
        if not username:
            username = text
    else:
        username = get_account(nick)
    if not username:
        return "No last.fm username specified and no last.fm username is set in the database."
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

    out = "{}'s favorite artists: ".format(username)
    for r in range(5):
        artist_name = data["topartists"]["artist"][r]["name"]
        play_count = data["topartists"]["artist"][r]["playcount"]
        out = out + "{} listened to {} times. ".format(artist_name, play_count)
    return out
