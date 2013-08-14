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

    out = u""

    try:
        out += soup.findAll('h1', {'class': 'header-title'})[1].text.strip()
    except Exception as e:
        print e
        return u"\x02Unable to retrieve info for %s!\x02 Is it a valid SteamCommunity profile username (%s)? " \
               "Check if your profile is private, or go here to search: %s" % (inp, web.try_isgd("http://steamcommunity.com/id/%s" % inp), web.try_isgd(url))

    nextone = False
    status = "Unknown"
    for i in soup.findAll('td'):
        if nextone:
            status = i.text
            break
        elif i.text == "Status":
            nextone=True
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
    out += " (%s)" % status

    for i in soup.findAll('div', {'class': 'panel'}):
        if str(i.find('div', {'class': 'panel-heading'})) == '<div class="panel-heading">Markdown</div>':
            data = i
    data = data.findAll('p')[1:]
    money = data[0].text.split(" ")[-1]
    totalgames = data[1].text.split(" ")[-1]
    notplayed = data[2].text.split(" ")[-1]
    nppercent = data[3].text.split(" ")[-1]
    time = data[4].text.split(" ")[-1].replace("h", "hours")
    out += " This account is worth \x02%s\x02, and they've spent \x02%s\x02 playing games! " % (money, time)
    out += " They have \x02%s games\x02, but \x02%s of them haven't been touched\x02! That's \x02%s\x02! " % (totalgames, notplayed, nppercent)

    if not dontsave:
        db.execute("insert or replace into steam(nick, acc) values (?,?)", (nick.lower(), inp))
        db.commit()

    return out + web.try_isgd(url)


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
