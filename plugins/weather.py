from util import hook, http, web

base_url = "http://api.wunderground.com/api/{}/geolookup/{}/q/{}.json"


@hook.command(autohelp=None)
def weather(inp, reply=None, db=None, nick=None, bot=None):
    "weather <location> [dontsave] -- Gets weather data"\
    " for <location> from Wunderground."

    api_key = bot.config.get("api_keys", {}).get("wunderground")

    if not api_key:
        return "Error: No wunderground API details."

    # initalise weather DB
    db.execute("create table if not exists weather(nick primary key, loc)")

    # if there is no input, try getting the users last location from the DB
    if not inp:
        location = db.execute("select loc from weather where nick=lower(?)",
                             [nick]).fetchone()
        if not location:
            # no location saved in the database, send the user help text
            notice(weather.__doc__)
            return
        loc = location[0]

        # no need to save a location, we already have it
        dontsave = True
    else:
        # see if the input ends with "dontsave"
        dontsave = inp.endswith(" dontsave")

        # remove "dontsave" from the input string after checking for it
        if dontsave:
            loc = inp[:-9].strip().lower()
        else:
            loc = inp

    location = http.quote_plus(loc)

    conditions_url = base_url.format(api_key, "conditions", location)
    conditions = http.get_json(conditions_url)

    try:
        conditions['location']['city']

        # found result, lets get the rest of the data
        forecast_url = base_url.format(api_key, "forecast", location)
        forecast = http.get_json(forecast_url)
    except KeyError:
        try:
            # try and get the closest match
            location_id = conditions['response']['results'][0]['zmw']
        except KeyError:
            return "Could not get weather for that location."

        # get the conditions again, using the closest match
        conditions_url = base_url.format(api_key, "conditions", "zmw:" + location_id)
        conditions = http.get_json(conditions_url)
        forecast_url = base_url.format(api_key, "forecast", "zmw:" + location_id)
        forecast = http.get_json(forecast_url)

    if conditions['location']['state']:
        place_name = "\x02{}\x02, \x02{}\x02 (\x02{}\x02)".format(conditions['location']['city'],
                                     conditions['location']['state'], conditions['location']['country'])
    else:
        place_name = "\x02{}\x02 (\x02{}\x02)".format(conditions['location']['city'],
                                      conditions['location']['country'])

    forecast_today = forecast["forecast"]["simpleforecast"]["forecastday"][0]
    forecast_tomorrow = forecast["forecast"]["simpleforecast"]["forecastday"][1]

    # put all the stuff we want to use in a dictionary for easy formatting of the output
    weather_data = {
        "place": place_name,
        "conditions": conditions['current_observation']['weather'],
        "temp_f": conditions['current_observation']['temp_f'],
        "temp_c": conditions['current_observation']['temp_c'],
        "humidity": conditions['current_observation']['relative_humidity'],
        "wind_kph": conditions['current_observation']['wind_kph'],
        "wind_mph": conditions['current_observation']['wind_mph'],
        "wind_direction": conditions['current_observation']['wind_dir'],
        "today_conditions": forecast_today['conditions'],
        "today_high_f": forecast_today['high']['fahrenheit'],
        "today_high_c": forecast_today['high']['celsius'],
        "today_low_f": forecast_today['low']['fahrenheit'],
        "today_low_c": forecast_today['low']['celsius'],
        "tomorrow_conditions": forecast_tomorrow['conditions'],
        "tomorrow_high_f": forecast_tomorrow['high']['fahrenheit'],
        "tomorrow_high_c": forecast_tomorrow['high']['celsius'],
        "tomorrow_low_f": forecast_tomorrow['low']['fahrenheit'],
        "tomorrow_low_c": forecast_tomorrow['low']['celsius'],
        "url": web.isgd(conditions["current_observation"]['forecast_url'] + "?apiref=e535207ff4757b18")
    }

    reply("{place} - \x02Current:\x02 {conditions}, {temp_f}F/{temp_c}C, {humidity}, "
          "Wind: {wind_kph}KPH/{wind_mph}MPH {wind_direction}, \x02Today:\x02 {today_conditions}, "
          "High: {today_high_f}F/{today_high_c}C, Low: {today_low_f}F/{today_low_c}C. "
          "\x02Tomorrow:\x02 {tomorrow_conditions}, High: {tomorrow_high_f}F/{tomorrow_high_c}C, "
          "Low: {tomorrow_low_f}F/{tomorrow_low_c}C - {url}".format(**weather_data))

    if location and not dontsave:
        db.execute("insert or replace into weather(nick, loc) values (?,?)",
                    (nick.lower(), location))
        db.commit()
