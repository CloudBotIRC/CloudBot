from util import hook
import yql


def get_weather(location_id):
    """uses the yahoo weather API to get weather information for a location"""

    y = yql.Public()
    query = 'select * from weather.forecast where woeid = "{}"'.format(location_id)
    data = y.execute(query).one()

    # wind conversions
    data['wind']['chill_c'] = int(round((int(data['wind']['chill']) - 32) / 1.8, 0))
    data['wind']['speed_kph'] = int(round(float(data['wind']['speed']) * 1.609344))

    # textual wind direction
    direction = data['wind']['direction']
    if direction >= 0 and direction < 45:
        data['wind']['text'] = 'N'
    elif direction >= 45 and direction < 90:
        data['wind']['text'] = 'NE'
    elif direction >= 90 and direction < 135:
        data['wind']['text'] = 'E'
    elif direction >= 135 and direction < 180:
        data['wind']['text'] = 'SE'
    elif direction >= 180 and direction < 225:
        data['wind']['text'] = 'S'
    elif direction >= 225 and direction < 270:
        data['wind']['text'] = 'SW'
    elif direction >= 270 and direction < 315:
        data['wind']['text'] = 'W'
    elif direction >= 315 and direction < 360:
        data['wind']['text'] = 'NW'
    else:
        data['wind']['text'] = 'N'

    # visibility and pressure conversions
    data['atmosphere']['visibility_km'] = \
        int(round(float(data['atmosphere']['visibility']) * 1.609344))
    data['atmosphere']['visibility_km'] = \
        str(round((float(data['atmosphere']['visibility']) * 33.8637526), 2))

    # textual value for air pressure
    rising = data['atmosphere']['rising']
    if rising == 0:
        data['atmosphere']['tendancy'] = 'steady'
    elif rising == 1:
        data['atmosphere']['tendancy'] = 'rising'
    elif rising == 2:
        data['atmosphere']['tendancy'] = 'falling'

    # current conditions
    data['item']['condition']['temp_c'] = \
        int(round(((float(data['item']['condition']['temp']) - 32) / 9) * 5))

    # forecasts
    for i in data['item']['forecast']:
        i['high_c'] = \
        int(round(((float(i['high']) - 32) / 9) * 5))
        i['low_c'] = \
        int(round(((float(i['high']) - 32) / 9) * 5))

    return data


@hook.command(autohelp=False)
def weather(inp, nick='', server='', reply=None, db=None, notice=None):
    "weather <location> [dontsave] -- Gets weather data"\
    " for <location> from Google."

    # initalise weather DB
    db.execute("create table if not exists y_weather(nick primary key, location_id)")

    # if there is no input, try getting the users last location from the DB
    if not inp:
        location_id = db.execute("select location_id from y_weather where nick=lower(?)",
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
        query = 'select * from geo.places where text = "{}" limit 1'.format(location)

        y = yql.Public()
        results = y.execute(query).one()
        location_id = results.get("woeid")

    # now, to get the actual weather
    d = get_weather(location_id)

    reply("Current Conditions for \x02{}\x02 - {}, {}F/{}C, {}%, " \
            "Wind: {}KPH/{}MPH {}.".format(d['location']['city'], \
            d['item']['condition']['text'], d['item']['condition']['temp'], \
            d['item']['condition']['temp_c'], d['atmosphere']['humidity'], \
             d['wind']['speed_kph'], d['wind']['speed'], d['wind']['text']))

    if location_id and not dontsave:
        db.execute("insert or replace into y_weather(nick, location_id) values (?,?)",
                     (nick.lower(), location_id))
        db.commit()
