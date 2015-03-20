import requests

from datetime import datetime
from bs4 import BeautifulSoup
from cloudbot import hook

user_url = "http://reddit.com/user/{}/"
subreddit_url = "http://reddit.com/r/{}/"
# This agent should be unique for your cloudbot instance
agent = {"User-Agent":"gonzobot a cloudbot (IRCbot) implementation for snoonet.org by /u/bloodygonzo"}

@hook.command("mods", "moderates", singlethreaded=True)
def moderates(text):
    """This plugin prints the list of subreddits a user moderates listed in a reddit users profile. Private subreddits will not be listed."""
    #This command was written using concepts from FurCode http://github.com/FurCode.
    user = text
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

@hook.command("karma", "ruser", singlethreaded=True)
def karma(text):
    """karma <reddituser> will return the information about the specified reddit username"""
    user = text
    url = user_url + "about.json"
    r = requests.get(url.format(user), headers=agent)
    if r.status_code != 200:
        return "Reddit returned an error, response: {}".format(r.status_code)
    data = r.json()
    out = "\x02{}\x02 ".format(user)
    out += "\x02{:,}\x02 link karma and ".format(data['data']['link_karma'])
    out += "\x02{:,}\x02 comment karma, ".format(data['data']['comment_karma'])
    if data['data']['is_gold']:
        out += "has reddit gold, "
    if data['data']['is_mod']:
        out += "is a moderator, "
    if data['data']['has_verified_email']:
        out += "email has been verified, "
    account_age = datetime.now() - datetime.fromtimestamp(data['data']['created'])
    if account_age.days > 365:
        age = int(account_age.days / 365)
        out += "and has been a redditor for {} years.".format(age)
    else:
        out += "and has been a redditor for {} days.".format(account_age.days)
    return out

@hook.command("submods", "rmods", singlethreaded=True)
def submods(text):
    """submods <subreddit> prints the moderators of the specified subreddit. Do not include /r/ when specifying a subreddit."""
    sub = text
    url = subreddit_url + "about/moderators.json"
    r = requests.get(url.format(sub), headers=agent)
    if r.status_code != 200:
        return "Reddit returned an error, response: {}".format(r.status_code)
    data = r.json()
    out = "r/\x02{}\x02 mods: ".format(sub)
    for mod in data['data']['children']:
        username = mod['name']
        # Showing the modtime makes the message too long for larger subs
        # if you want to show this information add modtime.days to out below
        # modtime = datetime.now() - datetime.fromtimestamp(mod['date'])
        out += "{} \u2022 ".format(username)
    out = out[:-3]
    return out

@hook.command("subinfo", "subreddit", singlethreaded=True)
def subinfo(text):
    """subinfo <subreddit> fetches information about the specified subreddit. Do not include /r/ when specifying a subreddit."""
    sub = text
    url = subreddit_url + "about.json"
    r = requests.get(url.format(sub), headers=agent)
    if r.status_code != 200:
        return "Reddit returned an error, response: {}".format(r.status_code)
    data = r.json()
    name = data['data']['display_name']
    title = data['data']['title']
    nsfw = data['data']['over18']
    subscribers = data['data']['subscribers']
    active = data['data']['accounts_active']
    sub_age = datetime.now() - datetime.fromtimestamp(data['data']['created'])
    age = ()
    if sub_age.days >= 365:
        age = (int(sub_age.days / 365), "year(s)")
    else:
        age = (sub_age.days, "days")
    out = "r/\x02{}\x02 - {} - Has been a community for {} {}, there are {:,} subscribers and {:,} people online now.".format(name, title, age[0], age[1], subscribers, active)
    if nsfw:
        out += " \x0304NSFW\x0304"
    return out
