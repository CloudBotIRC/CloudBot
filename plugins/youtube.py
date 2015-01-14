import re
import time
import isodate

import bs4
import requests

from cloudbot import hook
from cloudbot.util import timeformat
from cloudbot.util.formatting import pluralize


youtube_re = re.compile(r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)([-_a-zA-Z0-9]+)', re.I)

base_url = 'https://www.googleapis.com/youtube/v3/'
api_url = base_url + 'videos?part=contentDetails%2C+snippet%2C+statistics&id={}&key={}'
search_api_url = base_url + 'search?part=id&maxResults=1'
video_url = "http://youtu.be/%s"


def get_video_description(video_id, key):
    json = requests.get(api_url.format(video_id, key)).json()

    if json.get('error'):
        return

    data = json['items']
    snippet = data[0]['snippet']
    statistics = data[0]['statistics']
    content_details = data[0]['contentDetails']

    out = '\x02{}\x02'.format(snippet['title'])

    if not content_details.get('duration'):
        return out

    length = isodate.parse_duration(content_details['duration'])
    out += ' - length \x02{}\x02'.format(timeformat.format_time(int(length.total_seconds()), simple=True))

    if 'likeCount' in statistics:
        # format
        likes = pluralize(int(statistics['likeCount']), "like")
        dislikes = pluralize(int(statistics['dislikeCount']), "dislike")
        totalvotes = float(statistics['likeCount']) + float(statistics['dislikeCount'])

        percent = 100 * float(statistics['likeCount']) / totalvotes
        out += ' - {}, {} (\x02{:.1f}\x02%)'.format(likes,
                                                    dislikes, percent)

    if 'viewCount' in statistics:
        views = int(statistics['viewCount'])
        out += ' - \x02{:,}\x02 view{}'.format(views, "s"[views == 1:])

    uploader = snippet['channelTitle']

    upload_time = time.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%S.000Z")
    out += ' - \x02{}\x02 on \x02{}\x02'.format(uploader,
                                                time.strftime("%Y.%m.%d", upload_time))

    if 'contentRating' in content_details:
        out += ' - \x034NSFW\x02'

    return out


@hook.onload()
def load_key(bot):
    global dev_key
    dev_key = bot.config.get("api_keys", {}).get("google_dev_key")


@hook.regex(youtube_re)
def youtube_url(match, bot):
    return get_video_description(match.group(1), dev_key)


@hook.command("youtube", "you", "yt", "y")
def youtube(text):
    """youtube <query> -- Returns the first YouTube search result for <query>."""
    json = requests.get(search_api_url, params={"q": text, "key": dev_key}).json()

    if 'error' in json:
        return 'Error performing search.'

    if json['pageInfo']['totalResults'] == 0:
        return 'No results found.'

    video_id = json['items'][0]['id']['videoId']

    return get_video_description(video_id, dev_key) + " - " + video_url % video_id


@hook.command("youtime", "ytime")
def youtime(text):
    """youtime <query> -- Gets the total run time of the first YouTube search result for <query>."""
    json = requests.get(search_api_url, params={"q": text, "key": dev_key}).json()

    if 'error' in json:
        return 'Error performing search.'

    if json['pageInfo']['totalResults'] == 0:
        return 'No results found.'

    video_id = json['items'][0]['id']['videoId']
    json = requests.get(api_url.format(video_id, dev_key)).json()

    if json.get('error'):
        return
    data = json['items']
    snippet = data[0]['snippet']
    content_details = data[0]['contentDetails']
    statistics = data[0]['statistics']

    if not content_details.get('duration'):
        return

    length = isodate.parse_duration(content_details['duration'])
    l_sec = int(length.total_seconds())
    views = int(statistics['viewCount'])
    total = int(l_sec * views)

    length_text = timeformat.format_time(l_sec, simple=True)
    total_text = timeformat.format_time(total, accuracy=8)

    return 'The video \x02{}\x02 has a length of {} and has been viewed {:,} times for ' \
           'a total run time of {}!'.format(snippet['title'], length_text, views,
                                            total_text)


ytpl_re = re.compile(r'(.*:)//(www.youtube.com/playlist|youtube.com/playlist)(:[0-9]+)?(.*)', re.I)


@hook.regex(ytpl_re)
def ytplaylist_url(match):
    location = match.group(4).split("=")[-1]
    try:
        request = requests.get("https://www.youtube.com/playlist?list=" + location)
        soup = bs4.BeautifulSoup(request.text, 'lxml')
    except Exception:
        return "\x034\x02Invalid response."
    title = soup.find('title').text.split('-')[0].strip()
    author = soup.find('img', {'class': 'channel-header-profile-image'})['title']
    num_videos = soup.find('ul', {'class': 'header-stats'}).findAll('li')[0].text.split(' ')[0]
    views = soup.find('ul', {'class': 'header-stats'}).findAll('li')[1].text.split(' ')[0]
    return "\x02{}\x02 - \x02{}\x02 views - \x02{}\x02 videos - \x02{}\x02".format(title, views, num_videos, author)
