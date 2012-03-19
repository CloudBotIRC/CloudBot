"""
twitter.py: written by Scaevolus 2009, modified by Lukeroge 2012
retrieves most recent tweets
"""

import random
import re
from time import strptime, strftime
from datetime import datetime

from util import hook, http, timesince


def unescape_xml(string):
    # unescape the 5 chars that might be escaped in xml

    # gratuitously functional
    # return reduce(lambda x, y: x.replace(*y), (string,
    #     zip('&gt; &lt; &apos; &quote; &amp'.split(), '> < \' " &'.split()))

    # boring, normal
    return string.replace('&gt;', '>').replace('&lt;', '<').replace('&apos;',
                    "'").replace('&quote;', '"').replace('&amp;', '&')

history = []
history_max_size = 250

def parseDateTime(s):
    if s is None:
        return None
    m = re.match(r'(.*?)(?:\.(\d+))?(([-+]\d{1,2}):(\d{2}))?$',
                str(s))
    datestr, fractional, tzname, tzhour, tzmin = m.groups()

    if tzname is None:
        tz = None
    else:
        tzhour, tzmin = int(tzhour), int(tzmin)
        if tzhour == tzmin == 0:
            tzname = 'UTC'
        tz = FixedOffset(timedelta(hours=tzhour,
                                minutes=tzmin), tzname)
 
    x = datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
    if fractional is None:
        fractional = '0'
    fracpower = 6 - len(fractional)
    fractional = float(fractional) * (10 ** fracpower)

    return x.replace(microsecond=int(fractional), tzinfo=tz)


@hook.command
def twitter(inp):
    ".twitter <user>/<user> <n>/<id>/#<hashtag>/@<user> -- Gets last/<n>th "\
    "tweet from <user>/gets tweet <id>/Gets random tweet with #<hashtag>/"\
    "gets replied tweet from @<user>."

    def add_reply(reply_name, reply_id):
        if len(history) == history_max_size:
            history.pop()
        history.insert(0, (reply_name, reply_id))

    def find_reply(reply_name):
        for name, id in history:
            if name == reply_name:
                return id if id != -1 else name

    if inp[0] == '@':
        reply_inp = find_reply(inp[1:])
        if reply_inp == None:
            return 'No replies to %s found.' % inp
        inp = reply_inp

    url = 'http://twitter.com'
    getting_nth = False
    getting_id = False
    searching_hashtag = False

    time = 'status/created_at'
    text = 'status/text'
    reply_name = 'status/in_reply_to_screen_name'
    reply_id = 'status/in_reply_to_status_id'
    reply_user = 'status/in_reply_to_user_id'

    if re.match(r'^\d+$', inp):
        getting_id = True
        url += '/statuses/show/%s.xml' % inp
        screen_name = 'user/screen_name'
        time = 'created_at'
        text = 'text'
        reply_name = 'in_reply_to_screen_name'
        reply_id = 'in_reply_to_status_id'
        reply_user = 'in_reply_to_user_id'
    elif re.match(r'^\w{1,15}$', inp):
        url += '/users/show/%s.xml' % inp
        screen_name = 'screen_name'
    elif re.match(r'^\w{1,15}\s+\d+$', inp):
        getting_nth = True
        name, num = inp.split()
        if int(num) > 3200:
            return 'error: only supports up to the 3200th tweet'
        url += '/statuses/user_timeline/%s.xml?count=1&page=%s' % (name, num)
        screen_name = 'status/user/screen_name'
    elif re.match(r'^#\w+$', inp):
        url = 'http://search.twitter.com/search.atom?q=%23' + inp[1:]
        searching_hashtag = True
    else:
        return 'error: invalid request'

    try:
        tweet = http.get_xml(url)
    except http.HTTPError, e:
        errors = {400: 'bad request (ratelimited?)',
                401: 'tweet is private',
                403: 'tweet is private',
                404: 'invalid user/id',
                500: 'twitter is broken',
                502: 'twitter is down ("getting upgraded")',
                503: 'twitter is overloaded (lol, RoR)'}
        if e.code == 404:
            return 'error: invalid ' + ['username', 'tweet id'][getting_id]
        if e.code in errors:
            return 'error: ' + errors[e.code]
        return 'error: unknown %s' % e.code
    except http.URLerror, e:
        return 'error: timeout'

    if searching_hashtag:
        ns = '{http://www.w3.org/2005/Atom}'
        tweets = tweet.findall(ns + 'entry/' + ns + 'id')
        if not tweets:
            return 'Hashtag not found!'
        id = random.choice(tweets).text
        id = id[id.rfind(':') + 1:]
        return twitter(id)

    if getting_nth:
        if tweet.find('status') is None:
            return 'User doesn\'t have that many tweets!'

    time = tweet.find(time)
    if time is None:
        return 'User has no tweets!'

    reply_name = tweet.find(reply_name).text
    reply_id = tweet.find(reply_id).text
    reply_user = tweet.find(reply_user).text
    if reply_name is not None and (reply_id is not None or
            reply_user is not None):
        add_reply(reply_name, reply_id or -1)

    time_raw = strftime('%Y-%m-%d %H:%M:%S',
             strptime(time.text,
             '%a %b %d %H:%M:%S +0000 %Y'))

    time_pretty = timesince.timesince(parseDateTime(time_raw), datetime.utcnow())

    text = unescape_xml(tweet.find(text).text.replace('\n', ''))
    screen_name = tweet.find(screen_name).text

    return "\x02@%s\x02: %s (%s ago)" % (screen_name, text, time_pretty)
