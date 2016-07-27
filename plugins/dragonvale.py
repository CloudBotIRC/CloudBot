import requests
import re

from bs4 import BeautifulSoup
from cloudbot import hook
from cloudbot.util.timeparse import time_parse

search_url = "http://dragonvale.wikia.com/api/v1/Search/list"

egg_calc_url = "http://www.dragonvalebreedingguide.com/dragonvale-calculator"

def striphtml(data):
    string = re.compile(r'<.*?>')
    return string.sub('', data)

@hook.command("dragon", "ds")
def dragonsearch(text):
    """Searches the dragonvale wiki for the specified text."""
    params = {
        "query": text.strip(),
        "limit":1
    }

    r = requests.get(search_url, params=params)
    if not r.status_code == 200:
        return "The API returned error code {}.".format(r.status_code)

    data = r.json()["items"][0]
    out = "\x02{}\x02 -- {}: {}".format(data["title"], striphtml(data["snippet"]).split("&hellip;")[0].strip(), data["url"])
    return out

@hook.command("eggcalc", "dragoncalc", "dc")
def egg_calculator(text):
    """Parses dragonvalebreedingguide.com for a list of possible dragons based on the incubation time. Enter the time as 5 hours, 30 minutes. For upgraded incubation times put 'upgrade' at the front of the time length"""
    time = ""
    time2 = ""
    if text.lower().startswith("upgrade"):
        timer = text.replace("upgrade", "")
        time2 = time_parse(timer.strip())
        if not time2:
            return "invalid time format"
    else:
        timer = text
        time = time_parse(timer.strip())
        if not time:
            return "invalid time format"
    params = {
        'time': time,
        'time2': time2,
        'avail':1
    }
    r = requests.get(egg_calc_url, params=params, timeout=5)
    soup = BeautifulSoup(r.text)
    dragons = []
    for line in soup.findAll('td', {'class':'views-field views-field-title'}):
        dragons.append(line.text.replace("\n", "").strip())

    return ", ".join(dragons)
