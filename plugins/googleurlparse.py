from urllib.parse import unquote
import re
import requests

from cloudbot import hook

spamurl = re.compile(r'.*(((www\.)?google\.com/url\?|goo\.gl)[^ ]+)', re.I)


@hook.regex(spamurl)
def googleurl(match):
    matches = match.group(1)
    url = matches
    if "goo.gl/" in url:
        response = requests.get("http://{}".format(url))
        return response.url
    else:
        url = "http://{}".format(url)
        out = "".join([(unquote(a[4:]) if a[:4] == "url=" else "") for a in url.split("&")]) \
            .replace(", ,", "").strip()
        return out
