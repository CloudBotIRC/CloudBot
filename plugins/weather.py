"weather, thanks to google"
from util import hook, http


@hook.command(autohelp=False)
def forecast(inp, nick='', server='',
    reply=None, db=None, notice=None, say=None):
    ".forecast <location> [dontsave] -- Gets a weather forecast" \
    " for <location> from Google."
    loc = inp

    dontsave = loc.endswith(" dontsave")
    if dontsave:
        loc = loc[:-9].strip().lower()

    db.execute("create table if not exists weather(nick primary key, loc)")

    if not loc:
        loc = db.execute("select loc from weather where nick=lower(?)",
                            (nick,)).fetchone()
        if not loc:
            notice(forecast.__doc__)
            return
        loc = loc[0]

    w = http.get_xml('http://www.google.com/ig/api', weather=loc)
    w = w.find('weather')

    if w.find('problem_cause') is not None:
        notice("Couldn't fetch weather data for '%s', try using a zip or " \
                "postal code." % inp)
        return
    city = w.find('forecast_information/city').get('data')

    out = "%s: " % city

    for elem in w.findall('forecast_conditions'):
        info = dict((e.tag, e.get('data')) for e in elem)
        info['high'] = elem.find('high').get('data')
        info['low'] = elem.find('low').get('data')
        out += '[%(day_of_week)s]: %(condition)s (H:%(high)sF'\
            ', L:%(low)sF). ' % info

    return out


@hook.command(autohelp=False)
def weather(inp, nick='', server='', reply=None, db=None, notice=None):
    ".weather <location> [dontsave] -- Gets weather data"\
    " for <location> from Google."
    loc = inp

    dontsave = loc.endswith(" dontsave")
    if dontsave:
        loc = loc[:-9].strip().lower()

    db.execute("create table if not exists weather(nick primary key, loc)")

    if not loc:
        loc = db.execute("select loc from weather where nick=lower(?)",
                            (nick,)).fetchone()
        if not loc:
            notice(weather.__doc__)
            return
        loc = loc[0]

    w = http.get_xml('http://www.google.com/ig/api', weather=loc)
    w = w.find('weather')

    if w.find('problem_cause') is not None:
        notice("Couldn't fetch weather data for '%s', try using a zip or " \
                "postal code." % inp)
        return

    info = dict((e.tag, e.get('data')) for e in w.find('current_conditions'))
    info['city'] = w.find('forecast_information/city').get('data')
    info['high'] = w.find('forecast_conditions/high').get('data')
    info['low'] = w.find('forecast_conditions/low').get('data')

    reply('%(city)s: %(condition)s, %(temp_f)sF/%(temp_c)sC (H:%(high)sF'\
            ', L:%(low)sF), %(humidity)s, %(wind_condition)s.' % info)

    if inp and not dontsave:
        db.execute("insert or replace into weather(nick, loc) values (?,?)",
                     (nick.lower(), loc))
        db.commit()
