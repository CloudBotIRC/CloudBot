import datetime

from util import hook, http


base_url = "http://thetvdb.com/api/"
api_key = "469B73127CA0C411"


def get_episodes_for_series(series_name, api_key):
    res = {"error": None, "ended": False, "episodes": None, "name": None}
    # http://thetvdb.com/wiki/index.php/API:GetSeries
    try:
        query = http.get_xml(base_url + 'GetSeries.php', seriesname=series_name)
    except http.URLError:
        res["error"] = "error contacting thetvdb.com"
        return res

    series_id = query.xpath('//seriesid/text()')

    if not series_id:
        res["error"] = "Unknown TV series. (using www.thetvdb.com)"
        return res

    series_id = series_id[0]

    try:
        series = http.get_xml(base_url + '%s/series/%s/all/en.xml' % (api_key, series_id))
    except http.URLError:
        res["error"] = "Error contacting thetvdb.com."
        return res

    series_name = series.xpath('//SeriesName/text()')[0]

    if series.xpath('//Status/text()')[0] == 'Ended':
        res["ended"] = True

    res["episodes"] = series.xpath('//Episode')
    res["name"] = series_name
    return res


def get_episode_info(episode, api_key):
    first_aired = episode.findtext("FirstAired")

    try:
        air_date = datetime.date(*map(int, first_aired.split('-')))
    except (ValueError, TypeError):
        return None

    episode_num = "S%02dE%02d" % (int(episode.findtext("SeasonNumber")),
                                  int(episode.findtext("EpisodeNumber")))

    episode_name = episode.findtext("EpisodeName")
    # in the event of an unannounced episode title, users either leave the
    # field out (None) or fill it with TBA
    if episode_name == "TBA":
        episode_name = None

    episode_desc = '{}'.format(episode_num)
    if episode_name:
        episode_desc += ' - {}'.format(episode_name)
    return first_aired, air_date, episode_desc


@hook.command
@hook.command('tv')
def tv_next(inp, bot=None):
    """tv <series> -- Get the next episode of <series>."""

    api_key = bot.config.get("api_keys", {}).get("tvdb", None)
    if api_key is None:
        return "error: no api key set"
    episodes = get_episodes_for_series(inp, api_key)

    if episodes["error"]:
        return episodes["error"]

    series_name = episodes["name"]
    ended = episodes["ended"]
    episodes = episodes["episodes"]

    if ended:
        return "{} has ended.".format(series_name)

    next_eps = []
    today = datetime.date.today()

    for episode in reversed(episodes):
        ep_info = get_episode_info(episode, api_key)

        if ep_info is None:
            continue

        (first_aired, air_date, episode_desc) = ep_info

        if air_date > today:
            next_eps = ['{} ({})'.format(first_aired, episode_desc)]
        elif air_date == today:
            next_eps = ['Today ({})'.format(episode_desc)] + next_eps
        else:
            # we're iterating in reverse order with newest episodes last
            # so, as soon as we're past today, break out of loop
            break

    if not next_eps:
        return "There are no new episodes scheduled for {}.".format(series_name)

    if len(next_eps) == 1:
        return "The next episode of {} airs {}".format(series_name, next_eps[0])
    else:
        next_eps = ', '.join(next_eps)
        return "The next episodes of {}: {}".format(series_name, next_eps)


@hook.command
@hook.command('tv_prev')
def tv_last(inp, bot=None):
    """tv_last <series> -- Gets the most recently aired episode of <series>."""

    api_key = bot.config.get("api_keys", {}).get("tvdb", None)
    if api_key is None:
        return "error: no api key set"
    episodes = get_episodes_for_series(inp, api_key)

    if episodes["error"]:
        return episodes["error"]

    series_name = episodes["name"]
    ended = episodes["ended"]
    episodes = episodes["episodes"]

    prev_ep = None
    today = datetime.date.today()

    for episode in reversed(episodes):
        ep_info = get_episode_info(episode, api_key)

        if ep_info is None:
            continue

        (first_aired, air_date, episode_desc) = ep_info

        if air_date < today:
            #iterating in reverse order, so the first episode encountered
            #before today was the most recently aired
            prev_ep = '{} ({})'.format(first_aired, episode_desc)
            break

    if not prev_ep:
        return "There are no previously aired episodes for {}.".format(series_name)
    if ended:
        return '{} ended. The last episode aired {}.'.format(series_name, prev_ep)
    return "The last episode of {} aired {}.".format(series_name, prev_ep)
