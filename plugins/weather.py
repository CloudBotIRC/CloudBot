from util import hook, http

api_url = "http://weather.yahooapis.com/forecastrss"


def get_weather(location_id):
    """uses the yahoo weather API to get weather information for a location"""

    xml = http.get_xml(api_url, p=location_id)
    data = xml.xpath('//y:location', \
        namespaces={'y': 'http://xml.weather.yahoo.com/ns/rss/1.0'})[0]

    # create a dictionary for weather data
    weather = {}

    weather['city'] = data.get('city')
    weather['region'] = data.get('region')
    weather['country'] = data.get('country')

    # get wind information
    wind = xml.xpath('//y:wind', \
        namespaces={'y': 'http://xml.weather.yahoo.com/ns/rss/1.0'})[0]

    # wind chill
    weather['chill_f'] = wind.get('chill')
    weather['chill_c'] = int(round((int(wind.get('chill')) - 32) / 1.8, 0))

    # wind speed
    weather['wind_speed_kph'] = int(round(float(wind.get('speed')) * 1.609344))
    weather['wind_speed_mph'] = wind.get('speed')

    # wind_direction
    weather['wind_direction'] = wind.get('direction')

    # textual wind direction
    direction = weather['wind_direction']
    if direction >= 0 and direction < 45:
        weather['wind_direction_text'] = 'N'
    elif direction >= 45 and direction < 90:
        weather['wind_direction_text'] = 'NE'
    elif direction >= 90 and direction < 135:
        weather['wind_direction_text'] = 'E'
    elif direction >= 135 and direction < 180:
        weather['wind_direction_text'] = 'SE'
    elif direction >= 180 and direction < 225:
        weather['wind_direction_text'] = 'S'
    elif direction >= 225 and direction < 270:
        weather['wind_direction_text'] = 'SW'
    elif direction >= 270 and direction < 315:
        weather['wind_direction_text'] = 'W'
    elif direction >= 315 and direction < 360:
        weather['wind_direction_text'] = 'NW'
    else:
        weather['wind_direction_text'] = 'N'

    # humidity, visibility and pressure
    atmosphere = xml.xpath('//y:atmosphere', \
        namespaces={'y': 'http://xml.weather.yahoo.com/ns/rss/1.0'})[0]
    weather['humidity'] = atmosphere.get('humidity') + "%"
    weather['visibility_mi'] = atmosphere.get('visibility')
    weather['visibility_km'] = \
        int(round(float(atmosphere.get('visibility')) * 1.609344))
    weather['pressure_in'] = atmosphere.get('pressure')
    weather['pressure_mb'] = \
        str(round((float(atmosphere.get('pressure')) * 33.8637526), 2))

    # textual value for air pressure
    rising = int(atmosphere.get('rising'))
    if rising == 0:
        weather['pressure_tendancy'] = 'steady'
    elif rising == 1:
        weather['pressure_tendancy'] = 'rising'
    elif rising == 2:
        weather['pressure_tendancy'] = 'falling'

    # weather condition code, temperature, summary text
    condition = xml.xpath('//y:condition', \
        namespaces={'y': 'http://xml.weather.yahoo.com/ns/rss/1.0'})[0]
    weather['code'] = condition.get('code')
    weather['temp_f'] = condition.get('temp')
    weather['temp_c'] = \
        int(round(((float(condition.get('temp')) - 32) / 9) * 5))
    weather['conditions'] = condition.get('text')

    # sunset and sunrise
    sun = xml.xpath('//y:astronomy', \
        namespaces={'y': 'http://xml.weather.yahoo.com/ns/rss/1.0'})[0]
    weather['sunrise'] = sun.get('sunrise')
    weather['sunset'] = sun.get('sunset')

    return weather


@hook.command(autohelp=False)
def weather(inp, nick='', server='', reply=None, db=None, notice=None):
    "weather <location> [dontsave] -- Gets weather data"\
    " for <location> from Google."

    # initalise weather DB
    db.execute("create table if not exists yahoo_weather(nick primary key, location_id)")

    # if there is no input, try getting the users last location from the DB
    if not inp:
        location_id = db.execute("select location_id from yahoo_weather where nick=lower(?)",
                             [nick]).fetchone()
        if not location_id:
            # no location saved in the database, send the user help text
            notice(weather.__doc__)
            return
        location_id = location_id[0]

        # no need to save a location, we already have it
        dontsave = True
    else:
        # see if the input ends with "dontsave"
        dontsave = inp.endswith(" dontsave")

        # remove "dontsave" from the input string after checking for it
        if dontsave:
            location = inp[:-9].strip().lower()
        else:
            location = inp

        # get the weather.com location id from the location
        w = http.get_xml('http://xoap.weather.com/search/search', where=location)

        try:
            location_id = w.find('loc').get('id')
        except AttributeError:
            return "Unknown location."

    # now, to get the actual weather
    data = get_weather(location_id)

    reply('Current Conditions for \x02%(city)s\x02 - %(conditions)s, %(temp_f)sF/%(temp_c)sC, %(humidity)s, ' \
          'Wind: %(wind_speed_kph)sKPH/%(wind_speed_mph)sMPH %(wind_direction_text)s.' % data)

    if location_id and not dontsave:
        db.execute("insert or replace into yahoo_weather(nick, location_id) values (?,?)",
                     (nick.lower(), location_id))
        db.commit()