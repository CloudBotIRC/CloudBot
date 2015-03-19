# This plugin was written using concepts from FurCode http://github.com/FurCode.
import requests

from bs4 import BeautifulSoup
from cloudbot import hook

user_url = "http://reddit.com/user/{}/"
subreddit_url = "http://reddit.com/r/{}/"

@hook.command("mods", "moderates", singlethreaded=True)
def moderates(text):
    """This plugin prints the list of subreddits a user moderates listed in a reddit users profile. Private subreddits will not be listed."""
    user = text
    agent = {"User-Agent":"gonzobot a cloudbot implementation of an IRC bot for snoonet.org by /u/bloodygonzo"}

    r = requests.get(user_url.format(user), headers=agent)
    if r.status_code != 200:
        return "Reddit returned an error, response: {}".format(r.status_code)
    soup = BeautifulSoup(r.text)
    try:
        modlist = soup.find('ul', id="side-mod-list").text
    except:
        return "{} does not moderate any public subreddits.".format(user)
    modlist = modlist.split('/r/')
    del modlist[0]
    out = "\x02{}\x02 moderates these public channels: ".format(user)
    for sub in modlist:
        out += "{} \u2022 ".format(sub)
    out = out[:-2]
    return out
