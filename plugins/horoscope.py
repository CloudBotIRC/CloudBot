# Plugin by Infinity - <https://github.com/infinitylabs/UguuBot>

from util import hook, http, text

db_ready = False


def db_init(db):
    """check to see that our db has the horoscope table and return a connection."""
    global db_ready
    if not db_ready:
        db.execute("create table if not exists horoscope(nick primary key, sign)")
        db.commit()
        db_ready = True


@hook.command(autohelp=False)
def horoscope(inp, db=None, notice=None, nick=None):
    """horoscope <sign> -- Get your horoscope."""
    db_init(db)

    # check if the user asked us not to save his details
    dontsave = inp.endswith(" dontsave")
    if dontsave:
        sign = inp[:-9].strip().lower()
    else:
        sign = inp

    db.execute("create table if not exists horoscope(nick primary key, sign)")

    if not sign:
        sign = db.execute("select sign from horoscope where nick=lower(?)",
                          (nick,)).fetchone()
        if not sign:
            notice("horoscope <sign> -- Get your horoscope")
            return
        sign = sign[0]

    url = "http://my.horoscope.com/astrology/free-daily-horoscope-{}.html".format(sign)
    soup = http.get_soup(url)

    title = soup.find_all('h1', {'class': 'h1b'})[1]
    horoscope_text = soup.find('div', {'class': 'fontdef1'})
    result = u"\x02%s\x02 %s" % (title, horoscope_text)
    result = text.strip_html(result)
    #result = unicode(result, "utf8").replace('flight ','')

    if not title:
        return "Could not get the horoscope for {}.".format(inp)

    if inp and not dontsave:
        db.execute("insert or replace into horoscope(nick, sign) values (?,?)",
                    (nick.lower(), sign))
        db.commit()

    return result
