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

    # get author
    try:
        author_info = soup.find('ul', {'class': 'authorlinks'}).find('img')['alt']
        author = " - \x02{}\x02".format(author_info)
    except:
        author = ""

    # get rating
    try:
        rating_info = soup.find('dd', {'class': 'star-variable'})['title'].split("Stars &ndash;")[0].strip()
        rating = u" - rated \x02{}\x02/\x025.0\x02".format(rating_info)
    except:
        rating = ""

    # get amount of ratings
    try:
        ratings_info = soup.find('dd', {'class': 'star-variable'})['title'].split("Stars &ndash;")[1].replace("Votes",
                                                                                                              "").strip()
        numofratings = " ({})".format(ratings_info)
    except:
        numofratings = ""

    # get amount of views
    try:
        views_info = soup.find('dl', {'class': 'contentdata'}).findAll('dd')[1].find('strong').text
        views = " - \x02{}\x02 views".format(views_info)
    except:
        views = ""

    # get upload data
    try:
        date = "on \x02{}\x02".format(soup.find('dl', {'class': 'sidestats'}).find('dd').text)
    except:
        date = ""

    return title + rating + numofratings + views + author + date
