import requests
import re
from bs4 import BeautifulSoup
from contextlib import closing
from cloudbot import hook

# This will match any URL except the patterns defined in blacklist.
blacklist = '.*(reddit\.com|redd\.it|youtube\.com|youtu\.be|spotify\.com|twitter\.com|twitch\.tv|amazon\.co|xkcd\.com|amzn\.co|steamcommunity\.com|steampowered\.com|newegg\.com|soundcloud\.com|vimeo\.com).*'
url_re = re.compile('(?!{})http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'.format(blacklist), re.I)

opt_out = []

traditional = [
    (1024 ** 5, 'PB'),
    (1024 ** 4, 'TB'), 
    (1024 ** 3, 'GB'), 
    (1024 ** 2, 'MB'), 
    (1024 ** 1, 'KB'),
    (1024 ** 0, 'B'),
    ]


def bytesto(bytes, system = traditional):
    """ converts bytes to something """
    bytes = int(bytes)
    for factor, suffix in system:
        if bytes >= factor:
            break
    amount = int(bytes/factor)
    return str(amount) + suffix

@hook.regex(url_re)
def print_url_title(message, match, chan):
    if chan in opt_out:
        return
    HEADERS = {
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
    }
    with closing(requests.get(match.group(), headers = HEADERS, stream = True, timeout=3)) as r:
        if not r.encoding:
            # remove the content type and size from output for now
            r.close()
            return
            #content = r.headers['content-type']
            #size = bytesto(r.headers['content-length'])
            #out = "Content Type: \x02{}\x02 Size: \x02{}\x02".format(content, size)
            #return out
        content = r.raw.read(1000000+1, decode_content=True)
        if len(content) > 1000000:
            r.close()
            return
        html = BeautifulSoup(content)
        r.close()
        title = " ".join(html.title.text.strip().splitlines())
        out = "Title: \x02{}\x02".format(title)
        message(out, chan)
