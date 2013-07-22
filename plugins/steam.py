from util import hook, http, web, text, timesince
from urllib import urlencode
from datetime import datetime
import re


def shorten(inp):
    try:
        url = web.isgd(inp)
    except (web.ShortenError, http.HTTPError):
        url = inp
    return url

def db_init(db):
    db.execute("create table if not exists steam(nick primary key, acc)")
    db.commit()


@hook.command('sc', autohelp=False)
@hook.command(autohelp=False)
def steamcalc(inp, nick='', db=None):
    """steamcalc <username> [currency] - Gets value of steam account and
       total hours played. Uses steamcommunity.com/id/<nickname>. Uses
       IRC nickname if none provided. """
    currencies = {'USD': 'us', 'euro1': "de", 'euro2': 'no',
                  'pound': 'uk', 'rubles': 'ru', 'real': 'br',
                  'yen': 'jp', 'dollars': 'us', 'german': 'de',
                  'pounds': 'uk', 'russian': 'ru', 'brazil': 'br',
                  'japan': 'jp', 'us': 'us', 'de': 'de', 'no': 'no',
                  'uk': 'uk', 'ru': 'ru', 'br': 'br', 'jp': 'jp'}
    db_init(db)
    currency = None
    dontsave = False
    if not inp:
        user = db.execute("select acc from steam where nick=lower(?)", (nick,)).fetchone()
        if not user:
            inp = nick
        else:
            inp = user[0]
        dontsave = True
    else:
        if len(inp.split(" ")) > 1:
            if inp.split(" ")[1] in currencies:
                currency = currencies[inp.split(" ")[1]]
                dontsave = False
            elif inp.split(" ")[1] == "dontsave":
                dontsave = True
            else:
                return "Invalid currency!"
            inp = inp.split(" ")[0]
            if len(inp.split(" ")) > 2:
                if inp.split(" ")[2] == "dontsave":
                    dontsave = True
    urldata = urlencode({"player": inp, "currency": currency if currency else "us"})
    soup = http.get_soup("http://steamdb.info/calculator/?" + urldata)
    try:
        name = soup.findAll('h1', {'class': 'header-title'})[1].text
        status = soup.findAll('td')[7].text
    except Exception as e:
        print e
        return u"\x02Unable to retrieve info for %s!\x02 Is it a valid SteamCommunity profile username (%s)? " \
               "Check if your profile is private, or go here to search: %s" % (inp, shorten("http://steamcommunity.com/id/%s" % inp), shorten("http://steamdb.info/calculator/?" + urldata))
    if status == "Online":
        status = "\x033\x02Online\x02\x0f"
    elif status == "Offline":
        status = "\x034\x02Offline\x02\x0f"
    elif status == "Away":
        status = "\x038\x02Away\x02\x0f"
    elif status == "Busy":
        status = "\x035\x02Busy\x02\x0f"
    elif "Looking to" in status:
        status = "\x036\x02%s\x02\x0f" % status
    try:
        twdata = soup.find('h1', {'class': 'header-title pull-right'}).find('a')['data-text'].split(", ")
        money = twdata[0].split("My #Steam account is worth ")[1]
        time = twdata[1].split("and I spent ")[1].split(" playing games!")[0]
        worth = "This Steam account is worth \x02%s\x02, and they've spent \x02%s\x02 playing games! " % (money, time)
    except:
        worth = ""
    try:
        timeonsteam = soup.findAll('i')[1].text[1:-1].split(" ")
        timestamp = datetime.strptime(timeonsteam[0]+" "+timeonsteam[1]+" "+timeonsteam[2] + " - " + timeonsteam[4]+" "+timeonsteam[5], "%B %d, %Y - %H:%M:%S UTC")
        timeonsteam = timesince.timesince(timestamp)
        timeonsteam = "Their Steam account was created %s ago! " % timeonsteam
    except:
        timeonsteam = ""
    try:
        totalgames = soup.find('b').text
        notplayed = soup.findAll('b')[1].text
        nppercent = soup.findAll('i')[3].text[1:-1]
        gamesplayed = "They have \x02%s games in their Steam library\x02, but \x02%s of them haven't been touched\x02! That's \x02%s\x02! " % (totalgames, notplayed, nppercent)
    except:
        gamesplayed = ""
    if not dontsave:
        db.execute("insert or replace into steam(nick, acc) values (?,?)", (nick.lower(), inp))
        db.commit()
    if not worth and not timeonsteam and not gamesplayed:
        return "I couldn't read the information for that user. %s" % shorten("http://steamdb.info/calculator/?" + urldata)
    return u"%s (%s): %s%s%s%s" % (name, status, worth, timeonsteam, gamesplayed, shorten("http://steamdb.info/calculator/?" + urldata))
