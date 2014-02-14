from urllib import urlencode
import re

from util import hook, http, timeformat


hulu_re = (r'(.*://)(www.hulu.com|hulu.com)(.*)', re.I)


@hook.regex(*hulu_re)
def hulu_url(match):
    data = http.get_json("http://www.hulu.com/api/oembed.json?url=http://www.hulu.com" + match.group(3))
    showname = data['title'].split("(")[-1].split(")")[0]
    title = data['title'].split(" (")[0]
    return "{}: {} - {}".format(showname, title, timeformat.format_time(int(data['duration'])))


@hook.command('hulu')
def hulu_search(inp):
    """hulu <search> - Search Hulu"""
    result = http.get_soup(
        "http://m.hulu.com/search?dp_identifier=hulu&{}&items_per_page=1&page=1".format(urlencode({'query': inp})))
    data = result.find('results').find('videos').find('video')
    showname = data.find('show').find('name').text
    title = data.find('title').text
    duration = timeformat.format_time(int(float(data.find('duration').text)))
    description = data.find('description').text
    rating = data.find('content-rating').text
    return "{}: {} - {} - {} ({}) {}".format(showname, title, description, duration, rating,
                                             "http://www.hulu.com/watch/" + str(data.find('id').text))
