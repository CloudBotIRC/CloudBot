# Plugin by Infinity - <https://github.com/infinitylabs/UguuBot>

from util import hook, http

@hook.command
def horoscope(inp):
    "horoscope <sign> -- Get your horoscope."

    url = "http://my.horoscope.com/astrology/free-daily-horoscope-%s.html" % inp
    soup = http.get_soup(url)

    title = soup.find_all('h1', {'class': 'h1b'})[1]
    horoscope = soup.find('div', {'class': 'fontdef1'})
    result = "\x02%s\x02 %s" % (title, horoscope)
    result = http.strip_html(result)
    #result = unicode(result, "utf8").replace('flight ','')

    if not title:
        return "Could not get the horoscope for %s." % inp

    return result