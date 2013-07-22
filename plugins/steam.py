from util import hook, http, web, text
from urllib import urlencode
from datetime import datetime
import re

def db_init(db):
    db.execute("create table if not exists steam(nick primary key, acc)")
    db.commit()

def timesince(dt, default="just now"):
    now = datetime.utcnow()
    diff = now - dt
    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )
    for period, singular, plural in periods:
        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)
    return default

@hook.command('sc', autohelp=False)
@hook.command(autohelp=False)
    """steamcalc [username] [currency] - Gets value of steam account and total hours played. Uses steamcommunity.com/id/<nickname>. Uses IRC nickname if none provided. """
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
        else:
          return "Invalid currency!"
        inp = inp.split(" ")[0]
        dontsave = False
    urldata = urlencode({"player": inp, "currency": currency if currency else "us"})
    soup = http.get_soup("http://steamdb.info/calculator/?" + urldata)
    try:
      name = soup.findAll('h1', {'class': 'header-title'})[1].text
      status = soup.findAll('td')[7].text
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
      twdata = soup.find('h1', {'class': 'header-title pull-right'}).find('a')['data-text'].split(", ")
      money = twdata[0].split("My #Steam account is worth ")[1]
      time = twdata[1].split("and I spent ")[1].split(" playing games!")[0]
      timeonsteam = soup.findAll('i')[1].text[1:-1].split(" ")
      timestamp = datetime.strptime(timeonsteam[0]+" "+timeonsteam[1]+" "+timeonsteam[2] + " - " + timeonsteam[4]+" "+timeonsteam[5], "%B %d, %Y - %H:%M:%S UTC")
      timeonsteam = timesince(timestamp)
      totalgames = soup.find('b').text
      notplayed = soup.findAll('b')[1].text
      nppercent = soup.findAll('i')[3].text[1:-1]
      if not dontsave:
        db.execute("insert or replace into steam(nick, acc) values (?,?)", (nick.lower(), inp))
        db.commit()
      return u"%s (%s): This Steam account is worth \x02%s\x02, and they've spent \x02%s\x02 playing games! Their Steam account was created %s! They have \x02%s games in their Steam library\x02, but \x02%s of them haven't been touched\x02! That's %s! %s" % (name, status, money, time, timeonsteam, totalgames, notplayed, nppercent, web.isgd("http://steamdb.info/calculator/?"+ urldata))
    except Exception as e:
      print e
      return u"\x02Unable to retrieve info for %s!\x02 Check that it's a valid Steam profile username (steamcommunity.com/id/<USERNAME>), check if your profile is private, or go here to search: %s" % (inp, web.isgd("http://steamdb.info/calculator/?"+ urldata))
