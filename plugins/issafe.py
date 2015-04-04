"""
issafe.py

Check the Google Safe Browsing list to see a website's safety rating.

Created By:
    - Foxlet <http://furcode.tk/>

License:
    GNU General Public License (Version 3)
"""

from cloudbot import hook
import cloudbot
import requests
from urllib.parse import urlparse

API_SB = "https://sb-ssl.google.com/safebrowsing/api/lookup"


@hook.on_start()
def load_api(bot):
    global dev_key

    dev_key = bot.config.get("api_keys", {}).get("google_dev_key", None)

@hook.command()
def issafe(text):
    """<website> -- Checks the website against Google's Safe Browsing List."""
    if urlparse(text).scheme not in ['https', 'http']:
        return "Check your URL (it should be a complete URI)."

    parsed = requests.get(API_SB, params={"url": text, "client": "cloudbot", "key": dev_key, "pver": "3.1", "appver": str(cloudbot.__version__)})

    if parsed.status_code == 204:
        condition = "\x02{}\x02 is safe.".format(text)
    else:
        condition = "\x02{}\x02 is known to contain: {}".format(text, parsed.text)
    return condition