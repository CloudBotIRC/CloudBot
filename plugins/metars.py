import requests

from cloudbot import hook

api_url = "http://api.geonames.org/weatherIcaoJSON"

@hook.on_start()
def get_key(bot):
    """Gets the username to use in the geonames request"""
    global api_user
    api_user = bot.config.get("api_keys", {}).get("geonames")


@hook.command()
def metar(text):
    """metars [ICAO station code] returns the metars information for the specified station. A list of station codes can be found here: http://weather.rap.ucar.edu/surface/stations.txt"""
    if not api_user:
        return "no api_user has been specified."
    station = text.split(' ')[0].upper()
    if not len(station) == 4:
        return "please specify a valid station code see http://weather.rap.ucar.edu/surface/stations.txt for a list."
    params = {
        'username': api_user,
        'ICAO': station
    }
    request = requests.get(api_url, params=params)
    r = request.json()['weatherObservation']
    out = r['stationName'] + ": " + r['observation']
    return out
