"""
TV information, written by Lurchington 2010
modified by rmmh 2010
"""

import datetime
from urllib2 import URLError
from zipfile import ZipFile
from cStringIO import StringIO

from lxml import etree
from util import hook, http


base_url = "http://thetvdb.com/api/"
api_key = "469B73127CA0C411"


def get_zipped_xml(*args, **kwargs):
    try:
        path = kwargs.pop("path")
    except KeyError:
        raise KeyError("must specify a path for the zipped file to be read")
    zip_buffer = StringIO(http.get(*args, **kwargs))
    return etree.parse(ZipFile(zip_buffer, "r").open(path))


def get_episodes_for_series(seriesname):
    res = {"error": None, "ended": False, "episodes": None, "name": None}
    # http://thetvdb.com/wiki/index.php/API:GetSeries
    try:
        query = http.get_xml(base_url + 'GetSeries.php', seriesname=seriesname)
    except URLError:
        res["error"] = "error contacting thetvdb.com"
        return res

    series_id = query.xpath('//seriesid/text()')

    if not series_id:
        res["error"] = "unknown tv series (using www.thetvdb.com)"
        return res

    series_id = series_id[0]

    try:
        series = get_zipped_xml(base_url + '%s/series/%s/all/en.zip' %
                                    (api_key, series_id), path="en.xml")
    except URLError:
        res["error"] = "error contacting thetvdb.com"
        return res

    series_name = series.xpath('//SeriesName/text()')[0]

    if series.xpath('//Status/text()')[0] == 'Ended':
        res["ended"] = True

    res["episodes"] = series.xpath('//Episode')
    res["name"] = series_name
    return res


def get_episode_info(episode):
    first_aired = episode.findtext("FirstAired")

    try:
        airdate = datetime.date(*map(int, first_aired.split('-')))
    except (ValueError, TypeError):
        return None

    episode_num = "S%02dE%02d" % (int(episode.findtext("SeasonNumber")),
                                  int(episode.findtext("EpisodeNumber")))

    episode_name = episode.findtext("EpisodeName")
    # in the event of an unannounced episode title, users either leave the
    # field out (None) or fill it with TBA
    if episode_name == "TBA":
        episode_name = None

    episode_desc = '%s' % episode_num
    if episode_name:
        episode_desc += ' - %s' % episode_name
    return (first_aired, airdate, episode_desc)


@hook.command
@hook.command('tv')
def tv_next(inp):
    ".tv_next <series> -- get the next episode of <series>"
    episodes = get_episodes_for_series(inp)

    if episodes["error"]:
        return episodes["error"]

    series_name = episodes["name"]
    ended = episodes["ended"]
    episodes = episodes["episodes"]

    if ended:
        return "%s has ended." % series_name

    next_eps = []
    today = datetime.date.today()

    for episode in reversed(episodes):
        ep_info = get_episode_info(episode)

        if ep_info is None:
            continue

        (first_aired, airdate, episode_desc) = ep_info

        if airdate > today:
            next_eps = ['%s (%s)' % (first_aired, episode_desc)]
        elif airdate == today:
            next_eps = ['Today (%s)' % episode_desc] + next_eps
        else:
            #we're iterating in reverse order with newest episodes last
            #so, as soon as we're past today, break out of loop
            break

    if not next_eps:
        return "there are no new episodes scheduled for %s" % series_name

    if len(next_eps) == 1:
        return "the next episode of %s airs %s" % (series_name, next_eps[0])
    else:
        next_eps = ', '.join(next_eps)
        return "the next episodes of %s: %s" % (series_name, next_eps)


@hook.command
@hook.command('tv_prev')
def tv_last(inp):
    ".tv_last <series> -- gets the most recently aired episode of <series>"
    episodes = get_episodes_for_series(inp)

    if episodes["error"]:
        return episodes["error"]

    series_name = episodes["name"]
    ended = episodes["ended"]
    episodes = episodes["episodes"]

    prev_ep = None
    today = datetime.date.today()

    for episode in reversed(episodes):
        ep_info = get_episode_info(episode)

        if ep_info is None:
            continue

        (first_aired, airdate, episode_desc) = ep_info

        if airdate < today:
            #iterating in reverse order, so the first episode encountered
            #before today was the most recently aired
            prev_ep = '%s (%s)' % (first_aired, episode_desc)
            break

    if not prev_ep:
        return "there are no previously aired episodes for %s" % series_name
    if ended:
        return '%s ended. The last episode aired %s' % (series_name, prev_ep)
    return "the last episode of %s aired %s" % (series_name, prev_ep)
