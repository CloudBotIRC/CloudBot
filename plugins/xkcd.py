import re
from util import hook, http

xkcd_re = (r'(.*:)//(www.xkcd.com|xkcd.com)(.*)', re.I)

months = {'1': 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}


def xkcd_info(id, url=False):
    data = http.get_json("http://www.xkcd.com/" + id + "/info.0.json")
    date = "%s %s %s" % (data['day'], months[int(data['month'])], data['year'])
    if url:
        url = " | http://xkcd.com/" + id.replace("/", "")
    return "xkcd: \x02%s\x02 (%s)%s" % (data['title'], date, url if url else "")


def xkcd_search(inp):
    soup = http.get_soup("http://www.ohnorobot.com/index.pl?s=%s&Search=Search&comic=56&e=0&n=0&b=0&m=0&d=0&t=0" % inp)
    result = soup.find('li')
    if result:
        title = result.find('a').find('b').text
        url = result.find('div', {'class': 'tinylink'}).text
        id = url[:-1].split("/")[-1]
        return xkcd_info(id, url=True)
    else:
        return "No results found!"


@hook.regex(*xkcd_re)
def xkcd_url(match):
    id = match.group(3).split(" ")[0].split("/")[1]
    return xkcd_info(id)


@hook.command
def xkcd(inp):
    """xkcd <search term> - Search for xkcd comic matching <search term>"""
    return xkcd_search(inp)
