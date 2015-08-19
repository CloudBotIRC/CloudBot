import requests

from sqlalchemy import Table, Column, PrimaryKeyConstraint, String
from sqlalchemy.sql import select
from cloudbot import hook
from cloudbot.util import web, database


class APIError(Exception):
    pass

# Define database table

table = Table(
    "weather",
    database.metadata,
    Column('nick', String),
    Column('loc', String),
    PrimaryKeyConstraint('nick')
)

# Define some constants
google_base = 'https://maps.googleapis.com/maps/api/'
geocode_api = google_base + 'geocode/json'

wunder_api = "http://api.wunderground.com/api/{}/forecast/geolookup/conditions/q/{}.json"

# Change this to a ccTLD code (eg. uk, nz) to make results more targeted towards that specific country.
# <https://developers.google.com/maps/documentation/geocoding/#RegionCodes>
bias = None


def check_status(status):
    """
    A little helper function that checks an API error code and returns a nice message.
    Returns None if no errors found
    """
    if status == 'REQUEST_DENIED':
        return 'The geocode API is off in the Google Developers Console.'
    elif status == 'ZERO_RESULTS':
        return 'No results found.'
    elif status == 'OVER_QUERY_LIMIT':
        return 'The geocode API quota has run out.'
    elif status == 'UNKNOWN_ERROR':
        return 'Unknown Error.'
    elif status == 'INVALID_REQUEST':
        return 'Invalid Request.'
    elif status == 'OK':
        return None


def find_location(location):
    """
    Takes a location as a string, and returns a dict of data
    :param location: string
    :return: dict
    """
    params = {"address": location, "key": dev_key}
    if bias:
        params['region'] = bias

    json = requests.get(geocode_api, params=params).json()

    error = check_status(json['status'])
    if error:
        raise APIError(error)

    return json['results'][0]['geometry']['location']

def load_cache(db):
    global location_cache
    location_cache = []
    for row in db.execute(table.select()):
        nick = row["nick"]
        location = row["loc"]
        location_cache.append((nick,location))

def add_location(nick, location, db):
    test = dict(location_cache)
    location = str(location)
    if nick.lower() in test:
        db.execute(table.update().values(loc=location.lower()).where(table.c.nick == nick.lower()))
        db.commit()
        load_cache(db)
    else:
        db.execute(table.insert().values(nick=nick.lower(), loc=location.lower()))
        db.commit()
        load_cache(db)

@hook.on_start
def on_start(bot, db):
    """ Loads API keys """
    global dev_key, wunder_key
    dev_key = bot.config.get("api_keys", {}).get("google_dev_key", None)
    wunder_key = bot.config.get("api_keys", {}).get("wunderground", None)
    load_cache(db)


def get_location(nick):
    """looks in location_cache for a saved location"""
    location = [row[1] for row in location_cache if nick.lower() == row[0]]
    if not location:
        return
    else:
        location = location[0]
    return location

@hook.command("weather", "we", autohelp=False)
def weather(text, reply, db, nick, notice):
    """weather <location> -- Gets weather data for <location>."""
    if not wunder_key:
        return "This command requires a Weather Underground API key."
    if not dev_key:
        return "This command requires a Google Developers Console API key."

    location = ""
    # If no input try the db
    if not text:
        location = get_location(nick)
        if not location:
            notice(weather.__doc__)
            return
    else:
        location = text
    # use find_location to get location data from the user input
    try:
        location_data = find_location(location)
    except APIError as e:
        return e

    formatted_location = "{lat},{lng}".format(**location_data)

    url = wunder_api.format(wunder_key, formatted_location)
    response = requests.get(url).json()

    if response['response'].get('error'):
        return "{}".format(response['response']['error']['description'])

    forecast_today = response["forecast"]["simpleforecast"]["forecastday"][0]
    forecast_tomorrow = response["forecast"]["simpleforecast"]["forecastday"][1]

    # put all the stuff we want to use in a dictionary for easy formatting of the output
    weather_data = {
        "place": response['current_observation']['display_location']['full'],
        "conditions": response['current_observation']['weather'],
        "temp_f": response['current_observation']['temp_f'],
        "temp_c": response['current_observation']['temp_c'],
        "humidity": response['current_observation']['relative_humidity'],
        "wind_kph": response['current_observation']['wind_kph'],
        "wind_mph": response['current_observation']['wind_mph'],
        "wind_direction": response['current_observation']['wind_dir'],
        "today_conditions": forecast_today['conditions'],
        "today_high_f": forecast_today['high']['fahrenheit'],
        "today_high_c": forecast_today['high']['celsius'],
        "today_low_f": forecast_today['low']['fahrenheit'],
        "today_low_c": forecast_today['low']['celsius'],
        "tomorrow_conditions": forecast_tomorrow['conditions'],
        "tomorrow_high_f": forecast_tomorrow['high']['fahrenheit'],
        "tomorrow_high_c": forecast_tomorrow['high']['celsius'],
        "tomorrow_low_f": forecast_tomorrow['low']['fahrenheit'],
        "tomorrow_low_c": forecast_tomorrow['low']['celsius']
    }

    # Get the more accurate URL if available, if not, get the generic one.
    if "?query=," in response["current_observation"]['ob_url']:
        weather_data['url'] = web.shorten(response["current_observation"]['forecast_url'])
    else:
        weather_data['url'] = web.shorten(response["current_observation"]['ob_url'])

    reply("{place} - \x02Current:\x02 {conditions}, {temp_f}F/{temp_c}C, {humidity}, "
          "Wind: {wind_mph}MPH/{wind_kph}KPH {wind_direction}, \x02Today:\x02 {today_conditions}, "
          "High: {today_high_f}F/{today_high_c}C, Low: {today_low_f}F/{today_low_c}C. "
          "\x02Tomorrow:\x02 {tomorrow_conditions}, High: {tomorrow_high_f}F/{tomorrow_high_c}C, "
          "Low: {tomorrow_low_f}F/{tomorrow_low_c}C - {url}".format(**weather_data))
    if text:
        add_location(nick, location, db)
