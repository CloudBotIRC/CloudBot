import requests
import re
from bs4 import BeautifulSoup
from cloudbot import hook

# This will match ANY we url including youtube, reddit, twitch, etc... Some additional work needs to go into
# not sending the web request etc if the match also matches an existing web regex.
blacklist = re.compile('.*(reddit\.com|redd.it|youtube.com|youtu.be|spotify.com|twitter.com|twitch.com).*', re.I)
url_re = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


opt_in = []

@hook.regex(url_re)
def print_url_title(match, chan):
    if chan not in opt_in:
        return
    if re.search(blacklist, match.group()):
        return
    # It would be a good idea to also include useragent headers in the request
    r = requests.get(match.group())
    html = BeautifulSoup(r.text)
    title = html.title.text
    out = "Title: \x02{}\x02 at: \x02{}\x02".format(title, r.url)
    return out
