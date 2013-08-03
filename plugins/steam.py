from util import hook, http, web, text, timesince
from datetime import datetime
from bs4 import BeautifulSoup
import re

db_ready = False

steam_re = (r'(.*:)//(store.steampowered.com)(:[0-9]+)?(.*)', re.I)

currencies = {'USD': 'us', 'euro1': "de", 'euro2': 'no',
              'pound': 'uk', 'rubles': 'ru', 'real': 'br',
              'yen': 'jp', 'dollars': 'us', 'german': 'de',
              'pounds': 'uk', 'russian': 'ru', 'brazil': 'br',
              'japan': 'jp', 'us': 'us', 'de': 'de', 'no': 'no',
              'uk': 'uk', 'ru': 'ru', 'br': 'br', 'jp': 'jp'}


def db_init(db):
    db.execute("create table if not exists steam(nick primary key, acc)")
    db.commit()
    db_ready = True


@hook.command('sc', autohelp=False)
@hook.command(autohelp=False)
def steamcalc(inp, nick='', db=None):
    """steamcalc <username> [currency] - Gets value of steam account and
       total hours played. Uses steamcommunity.com/id/<nickname>. Uses
       IRC nickname if none provided. """

    if not db_ready:
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

    url = http.prepare_url("http://steamdb.info/calculator/", {"player": inp, "currency": currency if currency else "us"})
    soup = http.get_soup(url)

    try:
        name = soup.findAll('h1', {'class': 'header-title'})[1].text
        status = soup.findAll('td')[7].text
    except Exception as e:
        print e
        return u"\x02Unable to retrieve info for %s!\x02 Is it a valid SteamCommunity profile username (%s)? " \
               "Check if your profile is private, or go here to search: %s" % (inp, web.try_isgd("http://steamcommunity.com/id/%s" % inp), web.try_isgd(url))

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
        return "I couldn't read the information for that user. %s" % web.try_isgd(url)

    return u"%s (%s): %s%s%s%s" % (name.strip(), status, worth, timeonsteam, gamesplayed, web.try_isgd(url))


def get_steam_info(url):
    # we get the soup manually because the steam pages have some odd encoding troubles
    page = http.get(url)
    soup = BeautifulSoup(page, 'lxml', from_encoding="utf-8")

    name = soup.find('div', {'class': 'apphub_AppName'}).text
    desc = ": " + text.truncate_str(soup.find('div', {'class': 'game_description_snippet'}).text.strip())

    # the page has a ton of returns and tabs
    details = soup.find('div', {'class': 'glance_details'}).text.strip().split(u"\n\n\r\n\t\t\t\t\t\t\t\t\t")
    genre = " - Genre: " + details[0].replace(u"Genre: ", u"")
    date = " - Release date: " + details[1].replace(u"Release Date: ", u"")
    price = ""
    if not "Free to Play" in genre:
        price = " - Price: " + soup.find('div', {'class': 'game_purchase_price price'}).text.strip()

    return name + desc + genre + date + price


@hook.regex(*steam_re)
def steam_url(match):
    return get_steam_info("http://store.steampowered.com" + match.group(4))


@hook.command
def steam(inp):
    """steam [search] - Search for specified game/trailer/DLC"""
    page = http.get("http://store.steampowered.com/search/?term=" + inp)
    soup = BeautifulSoup(page, 'lxml', from_encoding="utf-8")
    result = soup.find('a', {'class': 'search_result_row'})
    return get_steam_info(result['href']) + " - " + web.isgd(result['href'])
