import requests
import re

from collections import defaultdict
from datetime import datetime
from bs4 import BeautifulSoup
from cloudbot import hook

search_pages = defaultdict(list)

user_url = "http://reddit.com/user/{}/"
subreddit_url = "http://reddit.com/r/{}/"
# This agent should be unique for your cloudbot instance
agent = {"User-Agent":"gonzobot a cloudbot (IRCbot) implementation for snoonet.org by /u/bloodygonzo"}


def two_lines(bigstring, chan):
    """Receives a string with new lines. Groups the string into a list of strings with up to 2 new lines per string element. Returns first string element then stores the remaining list in search_pages."""
    global search_pages
    temp = bigstring.split('\n')
    for i in range(0, len(temp), 2):
        search_pages[chan].append('\n'.join(temp[i:i+2]))
    search_pages[chan+"index"] = 0
    return search_pages[chan][0]


def smart_truncate(content, length=355, suffix='...\n'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' \u2022 ', 1)[0]+ suffix + content[:length].rsplit(' \u2022 ', 1)[1] + smart_truncate(content[length:])

def statuscheck(status, item):
    """since we are doing this a lot might as well return something more meaningful"""
    out = ""
    if status == 404:
        out = "It appears {} does not exist.".format(item)
    elif status == 403:
        out = "Sorry {} is set to private and I cannot access it.".format(item)
    elif status == 429:
        out = "Reddit appears to be rate-limiting me. Please try again in a few minutes."
    elif status == 503:
        out = "Reddit is having problems, it would be best to check back later."
    else:
        out = "Reddit returned an error, response: {}".format(status)
    return out

@hook.command("moremod", autohelp=False)
def moremod(text, chan):
    """if a sub or mod list has lots of results the results are pagintated. If the most recent search is paginated the pages are stored for retreival. If no argument is given the next page will be returned else a page number can be specified."""
    if not search_pages[chan]:
        return "There are modlist pages to show."
    if text:
        index = ""
        try:
            index = int(text)
        except:
            return "Please specify an integer value."
        if abs(int(index)) > len(search_pages[chan]) or index == 0:
            return "please specify a valid page number between 1 and {}.".format(len(search_pages[chan]))
        else:
            return "{}(page {}/{})".format(search_pages[chan][index-1], index, len(search_pages[chan]))
    else:
        search_pages[chan+"index"] += 1
        if search_pages[chan+"index"] < len(search_pages[chan]):
            return "{}(page {}/{})".format(search_pages[chan][search_pages[chan+"index"]], search_pages[chan+"index"] + 1, len(search_pages[chan]))
        else:
            return "All pages have been shown."


@hook.command("subs", "moderates", singlethreaded=True)
def moderates(text, chan):
    """This plugin prints the list of subreddits a user moderates listed in a reddit users profile. Private subreddits will not be listed."""
    #This command was written using concepts from FurCode http://github.com/FurCode.
    global search_pages
    search_pages[chan] = []
    search_pages[chan+"index"] = 0
    user = text
    r = requests.get(user_url.format(user), headers=agent)
    if r.status_code != 200:
        return statuscheck(r.status_code, user)
    soup = BeautifulSoup(r.text)
    try:
        modlist = soup.find('ul', id="side-mod-list").text
    except:
        return "{} does not moderate any public subreddits.".format(user)
    modlist = modlist.split('/r/')
    del modlist[0]
    out = "\x02{}\x02 moderates these public subreddits: ".format(user)
    for sub in modlist:
        out += "{} \u2022 ".format(sub)
    out = out[:-2]
    out = smart_truncate(out)
    if len(out.split('\n')) > 2:
        out = two_lines(out, chan)
        return "{}(page {}/{}) .moremod".format(out, search_pages[chan+"index"] + 1 , len(search_pages[chan]))
    return out


@hook.command("karma", "ruser", singlethreaded=True)
def karma(text):
    """karma <reddituser> will return the information about the specified reddit username"""
    user = text
    url = user_url + "about.json"
    r = requests.get(url.format(user), headers=agent)
    if r.status_code != 200:
        return statuscheck(r.status_code, user)
    data = r.json()
    out = "\x02{}\x02 ".format(user)
    out += "\x02{:,}\x02 link karma and ".format(data['data']['link_karma'])
    out += "\x02{:,}\x02 comment karma | ".format(data['data']['comment_karma'])
    if data['data']['is_gold']:
        out += "has reddit gold | "
    if data['data']['is_mod']:
        out += "is a moderator | "
    if data['data']['has_verified_email']:
        out += "email has been verified | "
    out += "cake day is {} | ".format(datetime.fromtimestamp(data['data']['created_utc']).strftime('%B %d') )
    account_age = datetime.now() - datetime.fromtimestamp(data['data']['created'])
    if account_age.days > 365:
        age = int(account_age.days / 365)
        if age == 1:
            out += "redditor for {} year.".format(age)
        else:
            out += "redditor for {} years.".format(age) 
    else:
        out += "redditor for {} days.".format(account_age.days)
    return out

@hook.command("cakeday", singlethreaded=True)
def cake_day(text):
    """cakeday <reddituser> will return the cakeday for the given reddit username."""
    user = text
    url = user_url + "about.json"
    r = requests.get(url.format(user), headers=agent)
    if r.status_code != 200:
        return statuscheck(r.status_code, user)
    data = r.json()
    out = "\x02{}'s\x02 ".format(user)
    out += "cake day is {}, ".format(datetime.fromtimestamp(data['data']['created_utc']).strftime('%B %d') )
    account_age = datetime.now() - datetime.fromtimestamp(data['data']['created'])
    if account_age.days > 365:
        age = int(account_age.days / 365)
        if age == 1:
            out += "they have been a redditor for {} year.".format(age)
        else:
            out += "they have been a redditor for {} years.".format(age)
    else:
        out += "they have been a redditor for {} days.".format(account_age.days)
    return out

def time_format(numdays):
    age = ()
    if numdays >= 365:
        age = (int(numdays / 365), "y")
        if age[0] > 1:
            age = (age[0], "y")
    else:
        age = (numdays, "d")
    return age

@hook.command("submods", "mods", "rmods", singlethreaded=True)
def submods(text, chan):
    """submods <subreddit> prints the moderators of the specified subreddit. Do not include /r/ when specifying a subreddit."""
    global search_pages
    search_pages[chan] = []
    search_pages[chan+"index"] = 0
    sub = text
    url = subreddit_url + "about/moderators.json"
    r = requests.get(url.format(sub), headers=agent)
    if r.status_code != 200:
        return statuscheck(r.status_code, 'r/'+sub)
    data = r.json()
    out = "r/\x02{}\x02 mods: ".format(sub)
    for mod in data['data']['children']:
        username = mod['name']
        # Showing the modtime makes the message too long for larger subs
        # if you want to show this information add modtime.days to out below
        modtime = datetime.now() - datetime.fromtimestamp(mod['date'])
        modtime = time_format(modtime.days)
        out += "{} ({}{}) \u2022 ".format(username, modtime[0], modtime[1])
    out = smart_truncate(out)
    out = out[:-3]
    if len(out.split('\n')) > 2:
        out = two_lines(out, chan)
        return "{}(page {}/{}) .moremod".format(out, search_pages[chan+"index"] + 1 , len(search_pages[chan]))
    return out

@hook.command("subinfo","subreddit", "sub", "rinfo", singlethreaded=True)
def subinfo(text):
    """subinfo <subreddit> fetches information about the specified subreddit. Do not include /r/ when specifying a subreddit."""
    sub = text
    url = subreddit_url + "about.json"
    r = requests.get(url.format(sub), headers=agent)
    if r.status_code != 200:
        return statuscheck(r.status_code, 'r/'+sub)
    data = r.json()
    if data['kind'] == "Listing":
        return "It appears r/{} does not exist.".format(sub)
    name = data['data']['display_name']
    title = data['data']['title']
    nsfw = data['data']['over18']
    subscribers = data['data']['subscribers']
    active = data['data']['accounts_active']
    sub_age = datetime.now() - datetime.fromtimestamp(data['data']['created'])
    age = ()
    if sub_age.days >= 365:
        age = (int(sub_age.days / 365), "y")
    else:
        age = (sub_age.days, "d")
    out = "r/\x03{}\x02 - {} - a community for {}{}, there are {:,} subscribers and {:,} people online now.".format(name, title, age[0], age[1], subscribers, active)
    if nsfw:
        out += " \x0304NSFW\x0304"
    return out
