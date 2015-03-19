"""
issafe.py

A plugin that uses the RRRather.com API to return random "Would you rather" questions.

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
    if urlparse(text).scheme == False:
        return "Check your URL (it should be a complete url)."

    parsed = requests.get(API_SB, params={"url": text, "client": "cloudbot", "key": dev_key, "pver": "3.1", "appver": str(cloudbot.__version__)})

    if parsed.status_code == 204:
        condition = "This website is safe."
    else:
        condition = "This site is known to contain: {}".format(parsed.text)
    return condition