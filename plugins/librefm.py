from datetime import datetime

import requests

from sqlalchemy import Table, Column, PrimaryKeyConstraint, String

from cloudbot import hook
from cloudbot.util import timeformat, web, database

api_url = "https://libre.fm/2.0/?format=json"

#Some of the libre.fm API calls do not have equivalent last.fm calls.
unsupported_msg = "This feature is not supported in the libre.fm API"

table = Table(
    "librefm",
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
    """looks in last_cache for the libre.fm account name"""
    last_account = [row[1] for row in last_cache if nick.lower() == row[0]]
    if not last_account:
        return
    else:
        last_account = last_account[0]
    return last_account


@hook.command("librefm", "librelast", "librenp", autohelp=False)
def librefm(text, nick, db, bot, notice):
    """[user] [dontsave] - displays the now playing (or last played) track of libre.fm user [user]"""

    # check if the user asked us not to save his details
    dontsave = text.endswith(" dontsave")
    if dontsave:
        user = text[:-9].strip().lower()
    else:
        user = text

    if not user:
        user = get_account(nick)
        if not user:
            notice(librefm.__doc__)
            return

    params = {'method': 'user.getrecenttracks',
                        'user': user, 'limit': 1}
    request = requests.get(api_url, params=params)

    if request.status_code != requests.codes.ok:
        return "Failed to fetch info ({})".format(request.status_code)

    response = request.json()

    if 'error' in response:
        #return "libre.fm Error: {}.".format(response["message"])
        return "libre.fm Error: {} Code: {}.".format(response["error"]["#text"], response["error"]["code"])

    if "track" not in response["recenttracks"] or len(response["recenttracks"]["track"]) == 0:
        return 'No recent tracks for user "{}" found.'.format(user)

    tracks = response["recenttracks"]["track"]

    if type(tracks) == list:
        track = tracks[0]

        if "@attr" in track and "nowplaying" in track["@attr"] and track["@attr"]["nowplaying"] == "true":
            # if the user is listening to something, the first track (a dict) of the
            # tracks list will contain an item with the "@attr" key.
            # this item will will contain another item with the "nowplaying" key
            # which value will be "true"
            status = 'is listening to'
            ending = '.'

    elif type(tracks) == dict:
        track = tracks
        # otherwise, the user is not listening to anything right now
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
    try:
        url = web.try_shorten(track["url"])
    except:
        url = track["url"]
        pass
    tags = getartisttags(artist, bot)

    out = '{} {} "{}"'.format(user, status, title)
    if artist:
        out += " by \x02{}\x0f".format(artist)
    if album:
        out += " from the album \x02{}\x0f".format(album)
    if url:
        out += " {}".format(url)

    out += " ({})".format(tags)

    # append ending based on what type it was
    out += ending

    if text and not dontsave:
        db.execute("insert or replace into librefm(nick, acc) values (:nick, :account)",
                   {'nick': nick.lower(), 'account': user})
        db.commit()
        load_cache(db)
    return out

def getartisttags(artist, bot):
    params = { 'method': 'artist.getTopTags', 'artist': artist }
    request = requests.get(api_url, params = params)
    tags = request.json()

    try:
        tag = tags['toptags']['tag']
    except:
        return 'no tags'
        pass

    if type(tag) == dict:
        tag_list = tag['name']
    elif type(tag) == list:
        tag_list = []
        for item in tag:
            tag_list.append(item['name'])
    else:
        return "error returning tags"

    if type(tag_list) == list:
        tag_list = tag_list[0:4]
        return ', '.join(tag_list)
    else:
        return tag_list

@hook.command("libreplays")
def getuserartistplaycount():
    """This command is not supported in the libre.fm API"""
    return unsupported_msg

@hook.command("libreband", "librela")
def displaybandinfo(text, nick, bot, notice):
    """[artist] - displays information about [artist]."""
    if not text:
        notice(getbandinfo.__doc__)
    artist = getartistinfo(text, bot)

    if 'error' in artist:
        return 'No such artist.'

    a = artist['artist']
    name = a["name"]
    summary = a["bio"]["summary"]
    tags = getartisttags(text, bot)

    try:
        url = web.try_shorten(a["url"])
    except:
        url = a["url"]
        pass

    out = "{}: ".format(a["name"])
    out += summary if summary else "No artist summary listed."
    out += " {}".format(url)
    out += " ({})".format(tags)

    return out

def getartistinfo(artist, bot, user = ''):
    params = { 'method': 'artist.getInfo', 'artist': artist,
            'autocorrect': '1'}
    if user:
        params['username'] = user
    request = requests.get(api_url, params = params);
    artist = request.json()
    return artist

@hook.command("librecompare", "librelc")
def librefmcompare(bot, text):
    """This command is not supported in the libre.fm API"""
    return unsupported_msg

@hook.command("libretoptrack", "libretoptracks", "libretop", "librett", autohelp=False)
def toptrack(text, nick, bot):
    """Grabs a list of the top tracks for a libre.fm username"""

    if text:
        username = get_account(text)
        if not username:
            username = text
    else:
        username = get_account(nick)
    if not username:
        return "No librefm username specified and no librefm username is set in the database."

    params = {
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
        out = out + "{} by {} listened to {:,} times. ".format(track_name, artist_name, int(play_count))
    return out

@hook.command("libretopartists", "libreta", autohelp=False)
def libretopartists(text, nick, bot):
    """Grabs a list of the top artists for a libre.fm username. You can set your libre.fm username with .librefm username"""
    if text:
        username = get_account(text)
        if not username:
            username = text
    else:
        username = get_account(nick)
    if not username:
        return "No libre.fm username specified and no libre.fm username is set in the database."

    params = {
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
        out = out + "{} listened to {:,} times. ".format(artist_name, int(play_count))
    return out


@hook.command("libreltw", "libretopweek", autohelp=False)
def topweek(text, nick, db, bot, notice):
    """Grabs a list of the top artists in the last week for a libre.fm username. You can set your librefm username with .l username"""
    topweek = topartists(text, nick, db, bot, notice, '7day')
    return topweek

@hook.command("libreltm", "libretopmonth", autohelp=False)
def topmonth(text, nick, db, bot, notice):
    """Grabs a list of the top artists in the last month for a libre.fm username. You can set your librefm username with .l username"""
    topmonth = topartists(text, nick, db, bot, notice, '1month')
    return topmonth

@hook.command("librelibrelta", "libretopall", autohelp=False)
def topall(text, nick, db, bot, notice):
    """Grabs a list of the top artists in the last year for a libre.fm username. You can set your librefm username with .l username"""
    topall = topartists(text, nick, db, bot, notice, '12month')
    return topall

def topartists(text, nick, db, bot, notice, period):
    if text:
        username = get_account(text)
        if not username:
            username = text
    else:
        username = get_account(nick)
    if not username:
        return("No librefm username specified and no librefm username is set in the database.")
    params = {
        'method': 'user.gettopartists',
        'user': username,
        'period': period,
        'limit': 10
    }
    request = requests.get(api_url, params=params)

    if request.status_code != requests.codes.ok:
        return "Failed to fetch info ({})".format(request.status_code)

    data = request.json()
    if 'error' in data:
        return data
        #return "Error: {}.".format(data["message"])

    if len(data["topartists"]["artist"]) < 10:
        range_count = len(data["topartists"]["artist"])
    else:
        range_count = 10

    out = "{}'s favorite artists: ".format(username)
    for r in range(range_count):
        artist_name = data["topartists"]["artist"][r]["name"]
        play_count = data["topartists"]["artist"][r]["playcount"]
        out = out + "{} [{:,}] ".format(artist_name, int(play_count))
    return out
