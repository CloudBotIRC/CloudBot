from util import hook, http, web

base_url = "http://api.wunderground.com/api/{}/{}/q/{}.json"


@hook.command(autohelp=None)
def weather(inp, reply=None, db=None, nick=None, bot=None, notice=None):
    """weather <location> [dontsave] -- Gets weather data
    for <location> from Wunderground."""

    api_key = bot.config.get("api_keys", {}).get("wunderground")

    if not api_key:
        return "Error: No wunderground API details."

    # initialise weather DB
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

    request_url = base_url.format(api_key, "geolookup/forecast/conditions", location)
    response = http.get_json(request_url)

    if 'location' not in response:
        try:
            location_id = response['response']['results'][0]['zmw']
        except KeyError:
            return "Could not get weather for that location."

        # get the weather again, using the closest match
        request_url = base_url.format(api_key, "geolookup/forecast/conditions", "zmw:" + location_id)
        response = http.get_json(request_url)

    if response['location']['state']:
        place_name = "\x02{}\x02, \x02{}\x02 (\x02{}\x02)".format(response['location']['city'],
                                                                  response['location']['state'],
                                                                  response['location']['country'])
    else:
        place_name = "\x02{}\x02 (\x02{}\x02)".format(response['location']['city'],
                                                      response['location']['country'])

    forecast_today = response["forecast"]["simpleforecast"]["forecastday"][0]
    forecast_tomorrow = response["forecast"]["simpleforecast"]["forecastday"][1]

    # put all the stuff we want to use in a dictionary for easy formatting of the output
    weather_data = {
        "place": place_name,
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
        "tomorrow_low_c": forecast_tomorrow['low']['celsius'],
        "url": web.isgd(response["current_observation"]['forecast_url'] + "?apiref=e535207ff4757b18")
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
