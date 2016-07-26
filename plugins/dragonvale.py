import requests
import re

from cloudbot import hook

search_url = "http://dragonvale.wikia.com/api/v1/Search/list"

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
