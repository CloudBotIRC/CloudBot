import re
import random
from datetime import datetime

import tweepy
from cloudbot import hook

from cloudbot.util import timeformat

TWITTER_RE = re.compile(r"(?:(?:www.twitter.com|twitter.com)/(?:[-_a-zA-Z0-9]+)/status/)([0-9]+)", re.I)


@hook.on_start()
def load_api(bot):
    global tw_api

    consumer_key = bot.config.get("api_keys", {}).get("twitter_consumer_key", None)
    consumer_secret = bot.config.get("api_keys", {}).get("twitter_consumer_secret", None)

    oauth_token = bot.config.get("api_keys", {}).get("twitter_access_token", None)
    oauth_secret = bot.config.get("api_keys", {}).get("twitter_access_secret", None)

    if not all((consumer_key, consumer_secret, oauth_token, oauth_secret)):
        tw_api = None
        return
    else:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(oauth_token, oauth_secret)

        tw_api = tweepy.API(auth)


@hook.regex(TWITTER_RE)
def twitter_url(match):
    # Find the tweet ID from the URL
    tweet_id = match.group(1)

    # Get the tweet using the tweepy API
    if tw_api is None:
        return

    try:
        tweet = tw_api.get_status(tweet_id)
        user = tweet.user
    except tweepy.error.TweepError:
        return

    # Format the return the text of the tweet
    text = " ".join(tweet.text.split())

    if user.verified:
        prefix = "\u2713"
    else:
        prefix = ""

    time = timeformat.time_since(tweet.created_at, datetime.utcnow())

    return "{}@\x02{}\x02 ({}): {} ({} ago)".format(prefix, user.screen_name, user.name, text, time)


@hook.command("twitter", "tw", "twatter")
def twitter(text):
    """twitter <user> [n] -- Gets last/[n]th tweet from <user>"""

    if tw_api is None:
        return "This command requires a twitter API key."

    if re.match(r'^\d+$', text):
        # user is getting a tweet by id

        try:
            # get tweet by id
            tweet = tw_api.get_status(text)
        except tweepy.error.TweepError as e:
            if "404" in e.reason:
                return "Could not find tweet."
            else:
                return "Error: {}".format(e.reason)

        user = tweet.user

    elif re.match(r'^\w{1,15}$', text) or re.match(r'^\w{1,15}\s+\d+$', text):
        # user is getting a tweet by name

        if text.find(' ') == -1:
            username = text
            tweet_number = 0
        else:
            username, tweet_number = text.split()
            tweet_number = int(tweet_number) - 1

        if tweet_number > 200:
            return "This command can only find the last \x02200\x02 tweets."

        try:
            # try to get user by username
            user = tw_api.get_user(username)
        except tweepy.error.TweepError as e:
            if "404" in e.reason:
                return "Could not find user."
            else:
                return "Error: {}".format(e.reason)

        # get the users tweets
        user_timeline = tw_api.user_timeline(id=user.id, count=tweet_number + 1)

        # if the timeline is empty, return an error
        if not user_timeline:
            return "The user \x02{}\x02 has no tweets.".format(user.screen_name)

        # grab the newest tweet from the users timeline
        try:
            tweet = user_timeline[tweet_number]
        except IndexError:
            tweet_count = len(user_timeline)
            return "The user \x02{}\x02 only has \x02{}\x02 tweets.".format(user.screen_name, tweet_count)

    elif re.match(r'^#\w+$', text):
        # user is searching by hashtag
        search = tw_api.search(text)

        if not search:
            return "No tweets found."

        tweet = random.choice(search)
        user = tweet.user
    else:
        # ???
        return "Invalid Input"

    # Format the return the text of the tweet
    text = " ".join(tweet.text.split())

    if user.verified:
        prefix = "\u2713"
    else:
        prefix = ""

    time = timeformat.time_since(tweet.created_at, datetime.utcnow())

    return "{}@\x02{}\x02 ({}): {} ({} ago)".format(prefix, user.screen_name, user.name, text, time)


@hook.command("twuser", "twinfo")
def twuser(text):
    """twuser <user> -- Get info on the Twitter user <user>"""

    if tw_api is None:
        return

    try:
        # try to get user by username
        user = tw_api.get_user(text)
    except tweepy.error.TweepError as e:
        if "404" in e.reason:
            return "Could not find user."
        else:
            return "Error: {}".format(e.reason)

    if user.verified:
        prefix = "\u2713"
    else:
        prefix = ""

    if user.location:
        loc_str = " is located in \x02{}\x02 and".format(user.location)
    else:
        loc_str = ""

    if user.description:
        desc_str = " The users description is \"{}\"".format(user.description)
    else:
        desc_str = ""

    return "{}@\x02{}\x02 ({}){} has \x02{:,}\x02 tweets and \x02{:,}\x02 followers.{}" \
           "".format(prefix, user.screen_name, user.name, loc_str, user.statuses_count, user.followers_count,
                     desc_str)
