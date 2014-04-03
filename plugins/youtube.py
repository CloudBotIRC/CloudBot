import re
import time

from util import hook, http, timeformat


youtube_re = (r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)'
              '([-_a-zA-Z0-9]+)', re.I)

base_url = 'http://gdata.youtube.com/feeds/api/'
api_url = base_url + 'videos/{}?v=2&alt=jsonc'
search_api_url = base_url + 'videos?v=2&alt=jsonc&max-results=1'
video_url = "http://youtu.be/%s"


def plural(num=0, text=''):
    return "{:,} {}{}".format(num, text, "s"[num == 1:])


def get_video_description(video_id):
    request = http.get_json(api_url.format(video_id))

    if request.get('error'):
        return

    data = request['data']

    out = u'\x02{}\x02'.format(data['title'])

    if not data.get('duration'):
        return out

    length = data['duration']
    out += u' - length \x02{}\x02'.format(timeformat.format_time(length, simple=True))

    if 'ratingCount' in data:
        likes = plural(int(data['likeCount']), "like")
        dislikes = plural(data['ratingCount'] - int(data['likeCount']), "dislike")

        percent = 100 * float(data['likeCount']) / float(data['ratingCount'])
        out += u' - {}, {} (\x02{:.1f}\x02%)'.format(likes,
                                                     dislikes, percent)

    if 'viewCount' in data:
        views = data['viewCount']
        out += u' - \x02{:,}\x02 view{}'.format(views, "s"[views == 1:])

    try:
        uploader = http.get_json(base_url + "users/{}?alt=json".format(data["uploader"]))["entry"]["author"][0]["name"][
            "$t"]
    except:
        uploader = data["uploader"]

    upload_time = time.strptime(data['uploaded'], "%Y-%m-%dT%H:%M:%S.000Z")
    out += u' - \x02{}\x02 on \x02{}\x02'.format(uploader,
                                                 time.strftime("%Y.%m.%d", upload_time))

    if 'contentRating' in data:
        out += u' - \x034NSFW\x02'

    return out


@hook.regex(*youtube_re)
def youtube_url(match):
    return get_video_description(match.group(1))


@hook.command('you')
@hook.command('yt')
@hook.command('y')
@hook.command
def youtube(inp):
    """youtube <query> -- Returns the first YouTube search result for <query>."""
    request = http.get_json(search_api_url, q=inp)

    if 'error' in request:
        return 'error performing search'

    if request['data']['totalItems'] == 0:
        return 'no results found'

    video_id = request['data']['items'][0]['id']

    return get_video_description(video_id) + u" - " + video_url % video_id


@hook.command('ytime')
@hook.command
def youtime(inp):
    """youtime <query> -- Gets the total run time of the first YouTube search result for <query>."""
    request = http.get_json(search_api_url, q=inp)

    if 'error' in request:
        return 'error performing search'

    if request['data']['totalItems'] == 0:
        return 'no results found'

    video_id = request['data']['items'][0]['id']
    request = http.get_json(api_url.format(video_id))

    if request.get('error'):
        return
    data = request['data']

    if not data.get('duration'):
        return

    length = data['duration']
    views = data['viewCount']
    total = int(length * views)

    length_text = timeformat.format_time(length, simple=True)
    total_text = timeformat.format_time(total, accuracy=8)

    return u'The video \x02{}\x02 has a length of {} and has been viewed {:,} times for ' \
           u'a total run time of {}!'.format(data['title'], length_text, views,
                                             total_text)


ytpl_re = (r'(.*:)//(www.youtube.com/playlist|youtube.com/playlist)(:[0-9]+)?(.*)', re.I)


@hook.regex(*ytpl_re)
def ytplaylist_url(match):
    location = match.group(4).split("=")[-1]
    try:
        soup = http.get_soup("https://www.youtube.com/playlist?list=" + location)
    except Exception:
        return "\x034\x02Invalid response."
    title = soup.find('title').text.split('-')[0].strip()
    author = soup.find('img', {'class': 'channel-header-profile-image'})['title']
    num_videos = soup.find('ul', {'class': 'header-stats'}).findAll('li')[0].text.split(' ')[0]
    views = soup.find('ul', {'class': 'header-stats'}).findAll('li')[1].text.split(' ')[0]
    return u"\x02%s\x02 - \x02%s\x02 views - \x02%s\x02 videos - \x02%s\x02" % (title, views, num_videos, author)
