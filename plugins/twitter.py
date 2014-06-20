import re
import random
from datetime import datetime

from twitter import Twitter, OAuth
from twitter.api import TwitterHTTPError

from cloudbot import hook
from cloudbot.util import timesince


@hook.onload()
def load_api(bot):
    global tw_api

    consumer_key = bot.config.get("api_keys", {}).get("twitter_consumer_key")
    consumer_secret = bot.config.get("api_keys", {}).get("twitter_consumer_secret")

    oauth_token = bot.config.get("api_keys", {}).get("twitter_access_token")
    oauth_secret = bot.config.get("api_keys", {}).get("twitter_access_secret")

    if None in (consumer_key, consumer_secret, oauth_token, oauth_secret):
        tw_api = None
        return
    else:
        tw_api = Twitter(auth=OAuth(oauth_token, oauth_secret, consumer_key, consumer_secret))


def format_tweet(tweet):
    user = tweet["user"]

    # Format the return the text of the tweet
    text = " ".join(tweet["text"].split())

    if user["verified"]:
        prefix = "\u2713"
    else:
        prefix = ""

    _time = timesince.timesince(datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'), datetime.utcnow())

    return "{}@\x02{}\x02 ({}): {} ({} ago)".format(prefix, user["screen_name"], user["name"], text, _time)


@hook.regex(re.compile(r"(?:(?:www.twitter.com|twitter.com)/(?:[-_a-zA-Z0-9]+)/status/)([0-9]+)", re.I))
def twitter_url(match):
    if tw_api is None:
        return

    # Find the tweet ID from the URL
    tweet_id = match.group(1)

    try:
        tweet = tw_api.statuses.show(_id=tweet_id)
    except TwitterHTTPError:
        return

    return format_tweet(tweet)


@hook.command("twitter", "tw", "twatter")
def twitter(text):
    """<user> [n] - gets the last/[n]th tweet from <user>"""

    if tw_api is None:
        return "Error: No Twitter API details."

    if re.match(r'^\d+$', text):
        # user is getting a tweet by id

        try:
            # get tweet by id
            tweet = tw_api.statuses.show(_id=text)
        except TwitterHTTPError as e:
            if e.e.code == 404:
                return "Could not find tweet."
            else:
                return "Error {}: {}".format(e.e.code, e.response_data)

    elif re.match(r'^\w{1,15}$', text) or re.match(r'^\w{1,15}\s+\d+$', text):
        # user is getting a tweet by name

        if ' ' in text:
            screen_name, tweet_number = text.split()
            tweet_number = int(tweet_number) - 1
        else:
            screen_name = text
            tweet_number = 0

        if tweet_number > 300:
            return "This command can only find the last \x02300\x02 tweets."

        try:
            # try to get user by username
            timeline = tw_api.statuses.user_timeline(screen_name=screen_name, count=tweet_number + 1)
        except TwitterHTTPError as e:
            if e.e.code == 404:
                return "Could not find user."
            else:
                return "Error {}: {}".format(e.e.code, e.response_data)

        # if the timeline is empty, return an error
        if not timeline:
            return "The user \x02{}\x02 has no tweets.".format(screen_name)

        # grab the newest tweet from the users timeline
        try:
            tweet = timeline[tweet_number]
        except IndexError:
            tweet_count = len(timeline)
            return "The user \x02{}\x02 only has \x02{}\x02 tweets.".format(screen_name, tweet_count)

    elif re.match(r'^#\w+$', text):
        # user is searching by hashtag
        search = tw_api.search.tweets(q=text)

        if not search:
            return "No tweets found."

        tweet = random.choice(search)
    else:
        # ???
        return "Invalid Input"

    # Format the return the text of the tweet
    return format_tweet(tweet)


@hook.command("twuser", "twinfo")
def twuser(text):
    """<user> - gets info on the Twitter user <user>"""

    if tw_api is None:
        return "Error: No Twitter API details."

    try:
        # try to get user by username
        user = tw_api.users.show(screen_name=text)
    except TwitterHTTPError as e:
        if e.e.code == 404:
            return "Could not find user."
        else:
            return "Error {}: {}".format(e.e.code, e.response_data)

    if user["verified"]:
        prefix = "\u2713"
    else:
        prefix = ""

    if user["location"]:
        loc_str = " is located in \x02{}\x02 and".format(user["location"])
    else:
        loc_str = ""

    if user["description"]:
        desc_str = " The users description is \"{}\"".format(user["description"])
    else:
        desc_str = ""

    return "{}@\x02{}\x02 ({}){} has \x02{:,}\x02 tweets and \x02{:,}\x02 followers.{}".format(
        prefix, user["screen_name"], user["name"], loc_str, user["statuses_count"], user["followers_count"], desc_str)
