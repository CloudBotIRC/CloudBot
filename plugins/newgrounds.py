import re
from util import hook, http

newgrounds_re = (r'(.*:)//(www.newgrounds.com|newgrounds.com)(:[0-9]+)?(.*)', re.I)
valid = set('0123456789')


def test(s):
    return set(s) <= valid


@hook.regex(*newgrounds_re)
def newgrounds_url(match):
    location = match.group(4).split("/")[-1]
    if not test(location):
        print "Not a valid Newgrounds portal ID. Example: http://www.newgrounds.com/portal/view/593993"
        return None
    soup = http.get_soup("http://www.newgrounds.com/portal/view/" + location)
    title = "\x02{}\x02".format(soup.find('title').text)
    try:
        author = " - \x02{}\x02".format(soup.find('ul', {'class': 'authorlinks'}).find('img')['alt'])
    except:
        author = ""

    try:
        rating = u" - rated \x02%s\x02/\x025.0\x02" % soup.find('dd', {'class': 'star-variable'})['title'].split("Stars &ndash;")[0].strip()
    except:
        rating = ""

    try:
        numofratings = " ({})".format(soup.find('dd', {'class': 'star-variable'})['title'].split("Stars &ndash;")[1].replace("Votes", "").strip())
    except:
        numofratings = ""

    try:
        views = " - \x02{}\x02 views".format(soup.find('dl', {'class': 'contentdata'}).findAll('dd')[1].find('strong').text)
    except:
        views = ""

    try:
        date = "on \x02{}\x02".format(soup.find('dl', {'class': 'sidestats'}).find('dd').text)
    except:
        date = ""
    return title + rating + numofratings + views + author + date
