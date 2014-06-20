# Plugin by Infinity - <https://github.com/infinitylabs/UguuBot>

from cloudbot import hook
from cloudbot.util import http, formatting


@hook.onload()
def init(db):
    db.execute("create table if not exists horoscope(nick primary key, sign)")
    db.commit()


@hook.command(autohelp=False)
def horoscope(text, db, notice, nick):
    """<sign> - get your horoscope"""

    # check if the user asked us not to save his details
    dontsave = text.endswith(" dontsave")
    if dontsave:
        sign = text[:-9].strip().lower()
    else:
        sign = text

    db.execute("create table if not exists horoscope(nick primary key, sign)")

    if not sign:
        sign = db.execute("select sign from horoscope where "
                          "nick=lower(:nick)", {'nick': nick}).fetchone()
        if not sign:
            notice("horoscope <sign> -- Get your horoscope")
            return
        sign = sign[0]

    url = "http://my.horoscope.com/astrology/free-daily-horoscope-{}.html".format(sign)
    soup = http.get_soup(url)

    title = soup.find_all('h1', {'class': 'h1b'})[1]
    horoscope_text = soup.find('div', {'class': 'fontdef1'})
    result = "\x02{}\x02 {}".format(title, horoscope_text)
    result = formatting.strip_html(result)
    # result = unicode(result, "utf8").replace('flight ','')

    if not title:
        return "Could not get the horoscope for {}.".format(text)

    if text and not dontsave:
        db.execute("insert or replace into horoscope(nick, sign) values (:nick, :sign)",
                   {'nick': nick.lower(), 'sign': sign})
        db.commit()

    return result
