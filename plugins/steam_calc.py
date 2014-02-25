import csv
import StringIO

from util import hook, http, text


gauge_url = "http://www.mysteamgauge.com/search?username={}"

api_url = "http://mysteamgauge.com/user/{}.csv"
steam_api_url = "http://steamcommunity.com/id/{}/?xml=1"


def refresh_data(name):
    http.get(gauge_url.format(name), timeout=25, get_method='HEAD')


def get_data(name):
    return http.get(api_url.format(name))


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def unicode_dictreader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield dict([(key.lower(), unicode(value, 'utf-8')) for key, value in row.iteritems()])


@hook.command('sc')
@hook.command
def steamcalc(inp, reply=None):
    """steamcalc <username> [currency] - Gets value of steam account and
       total hours played. Uses steamcommunity.com/id/<nickname>. """

    # check if the user asked us to force reload
    force_reload = inp.endswith(" forcereload")
    if force_reload:
        name = inp[:-12].strip().lower()
    else:
        name = inp.strip()

    if force_reload:
        try:
            reply("Collecting data, this may take a while.")
            refresh_data(name)
            request = get_data(name)
            do_refresh = False
        except (http.HTTPError, http.URLError):
            return "Could not get data for this user."
    else:
        try:
            request = get_data(name)
            do_refresh = True
        except (http.HTTPError, http.URLError):
            try:
                reply("Collecting data, this may take a while.")
                refresh_data(name)
                request = get_data(name)
                do_refresh = False
            except (http.HTTPError, http.URLError):
                return "Could not get data for this user."

    csv_data = StringIO.StringIO(request)  # we use StringIO because CSV can't read a string
    reader = unicode_dictreader(csv_data)

    # put the games in a list
    games = []
    for row in reader:
        games.append(row)

    data = {}

    # basic information
    steam_profile = http.get_xml(steam_api_url.format(name))
    try:
        data["name"] = steam_profile.find('steamID').text
        online_state = steam_profile.find('stateMessage').text
    except AttributeError:
        return "Could not get data for this user."

    online_state = online_state.replace("<br/>", ": ")  # will make this pretty later
    data["state"] = text.strip_html(online_state)

    # work out the average metascore for all games
    ms = [float(game["metascore"]) for game in games if is_number(game["metascore"])]
    metascore = float(sum(ms)) / len(ms) if len(ms) > 0 else float('nan')
    data["average_metascore"] = "{0:.1f}".format(metascore)

    # work out the totals
    data["games"] = len(games)

    total_value = sum([float(game["value"]) for game in games if is_number(game["value"])])
    data["value"] = str(int(round(total_value)))

    # work out the total size
    total_size = 0.0

    for game in games:
        if not is_number(game["size"]):
            continue

        if game["unit"] == "GB":
            total_size += float(game["size"])
        else:
            total_size += float(game["size"]) / 1024

    data["size"] = "{0:.1f}".format(total_size)

    reply("{name} ({state}) has {games} games with a total value of ${value}"
          " and a total size of {size}GB! The average metascore for these"
          " games is {average_metascore}.".format(**data))

    if do_refresh:
        refresh_data(name)
