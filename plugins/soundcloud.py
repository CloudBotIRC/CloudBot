import re
import requests
from pprint import pprint

from cloudbot import hook
from cloudbot.util import http, web, formatting

SC_RE = re.compile(r'(.*:)//(www.)?(soundcloud.com|snd.sc)(.*)', re.I)
API_BASE = "http://api.soundcloud.com/{}/"


class APIError(Exception):
    pass


# DATA FETCHING
def get_with_search(term):
    """
    Takes a search term and finds a track on SoundCloud. Will only return 'track' items.
    :param term:
    :return:
    """
    try:
        params = {'q': term, 'client_id': api_key}
        request = requests.get(API_BASE.format('tracks'), params=params)
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise APIError("Could not find track: {}".format(e))

    json = request.json()

    if not json:
        return None
    else:
        return json[0]


def get_with_url(url):
    """
    Takes a SoundCloud URL and returns an item. Can return any item type.
    :param url:
    :return:
    """


# DATA FORMATTING
def format_track(track, show_url=True):
    """
    Takes a SoundCloud track item and returns a formatted string.
    :type show_url: object
    :param track:
    :return:
    """
    out = ""
    out += track['title']

    out += " by \x02{}\x02".format(track['user']['username'])

    if track['genre']:
        out += " - \x02{}\x02".format(track['genre'])

    out += " - \x02{:,}\x02 plays, \x02{:,}\x02 downloads, \x02{:,}\x02 comments".format(track['playback_count'],
                                                                                         track['download_count'],
                                                                                         track['comment_count'])

    if show_url:
        out += " - {}".format(web.try_shorten(track['permalink_url']))
    return out


# CLOUDBOT HOOKS
@hook.on_start()
def load_key(bot):
    global api_key
    api_key = bot.config.get("api_keys", {}).get("soundcloud", None)


@hook.command("soundcloud")
def soundcloud(text):
    if not api_key:
        return "This command requires a SoundCloud API key."
    try:
        track = get_with_search(text)
    except APIError as ae:
        return ae

    if not track:
        return "No results found."

    try:
        return format_track(track)
    except APIError as ae:
        return ae

