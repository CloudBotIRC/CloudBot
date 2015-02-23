import requests

from cloudbot import hook
from cloudbot.util import web


# Define some constants
google_base = 'https://maps.googleapis.com/maps/api/'
geocode_api = google_base + 'geocode/json'

wunder_api = "http://api.wunderground.com/api/{}/forecast/geolookup/conditions/q/{}.json"

# Change this to a ccTLD code (eg. uk, nz) to make results more targeted towards that specific country.
# <https://developers.google.com/maps/documentation/geocoding/#RegionCodes>
bias = None


def check_status(status):
    """ A little helper function that checks an API error code and returns a nice message.
        Returns None if no errors found """
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
    else:
        # !!!
        return 'Unknown Demons.'


def get_location(text, nick, conn, db):
    # initialise weather DB
    db.execute("create table if not exists weather(nick primary key, loc)")

    # if there is no input, try getting the users last location from the DB
    if not text:
        location = db.execute("select loc from weather where nick=lower(:nick)",
                              {"nick": nick}).fetchone()
        if not location:
            # no location saved in the database
            return None

        return location[0]

        # no need to save a location, we already have it
        dontsave = True
    else:
        # see if the input ends with "dontsave"
        dontsave = text.endswith(" dontsave")

        # remove "dontsave" from the input string after checking for it
        if dontsave:
            return text[:-9].strip().lower()
        else:
            return text


@hook.on_start
def load_keys(bot):
    """ Loads API keys """
    global dev_key, wunder_key
    dev_key = bot.config.get("api_keys", {}).get("google_dev_key", None)
    wunder_key = bot.config.get("api_keys", {}).get("wunderground", None)


@hook.command("xx", "we", autohelp=False)
def weather2(text, reply, db, nick, bot, notice):
    """weather <location> [dontsave] -- Gets weather data
    for <location> from Wunderground."""

    if not wunder_key:
        return "This command requires a Weather Underground API key."
    if not dev_key:
        return "This command requires a Google Developers Console API key."

    # Use the Geocoding API to get co-ordinates from the input
    params = {"address": text, "key": dev_key}
    if bias:
        params['region'] = bias

    json = requests.get(geocode_api, params=params).json()

    error = check_status(json['status'])
    if error:
        return error
    location = json['results'][0]['geometry']['location']

    # Now we have the co-ordinates, we use the Wunderground API to get the weather
    formatted_location = "{lat},{lng}".format(**location)

    url = wunder_api.format(wunder_key, formatted_location)
    print(url)
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
          "Wind: {wind_kph}KPH/{wind_mph}MPH {wind_direction}, \x02Today:\x02 {today_conditions}, "
          "High: {today_high_f}F/{today_high_c}C, Low: {today_low_f}F/{today_low_c}C. "
          "\x02Tomorrow:\x02 {tomorrow_conditions}, High: {tomorrow_high_f}F/{tomorrow_high_c}C, "
          "Low: {tomorrow_low_f}F/{tomorrow_low_c}C - {url}".format(**weather_data))