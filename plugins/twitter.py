import re
import random
from datetime import datetime

import tweepy

from util import hook, timesince


TWITTER_RE = (r"(?:(?:www.twitter.com|twitter.com)/(?:[-_a-zA-Z0-9]+)/status/)([0-9]+)", re.I)


def get_api(bot):
    consumer_key = bot.config.get("api_keys", {}).get("twitter_consumer_key")
    consumer_secret = bot.config.get("api_keys", {}).get("twitter_consumer_secret")

    oauth_token = bot.config.get("api_keys", {}).get("twitter_access_token")
    oauth_secret = bot.config.get("api_keys", {}).get("twitter_access_secret")

    if not consumer_key:
        return False

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(oauth_token, oauth_secret)

    return tweepy.API(auth)


@hook.regex(*TWITTER_RE)
def twitter_url(match, bot=None):
    # Find the tweet ID from the URL
    tweet_id = match.group(1)

    # Get the tweet using the tweepy API
    api = get_api(bot)
    if not api:
        return
    try:
        tweet = api.get_status(tweet_id)
        user = tweet.user
    except tweepy.error.TweepError:
        return

    # Format the return the text of the tweet
    text = " ".join(tweet.text.split())

    if user.verified:
        prefix = u"\u2713"
    else:
        prefix = ""

    time = timesince.timesince(tweet.created_at, datetime.utcnow())

    return u"{}@\x02{}\x02 ({}): {} ({} ago)".format(prefix, user.screen_name, user.name, text, time)


@hook.command("tw")
@hook.command("twatter")
@hook.command
def twitter(inp, bot=None):
    """twitter <user> [n] -- Gets last/[n]th tweet from <user>"""

    api = get_api(bot)
    if not api:
        return "Error: No Twitter API details."

    if re.match(r'^\d+$', inp):
        # user is getting a tweet by id

        try:
            # get tweet by id
            tweet = api.get_status(inp)
        except tweepy.error.TweepError as e:
            if e[0][0]['code'] == 34:
                return "Could not find tweet."
            else:
                return u"Error {}: {}".format(e[0][0]['code'], e[0][0]['message'])

        user = tweet.user

    elif re.match(r'^\w{1,15}$', inp) or re.match(r'^\w{1,15}\s+\d+$', inp):
        # user is getting a tweet by name

        if inp.find(' ') == -1:
            username = inp
            tweet_number = 0
        else:
            username, tweet_number = inp.split()
            tweet_number = int(tweet_number) - 1

        if tweet_number > 300:
            return "This command can only find the last \x02300\x02 tweets."

        try:
            # try to get user by username
            user = api.get_user(username)
        except tweepy.error.TweepError as e:
            if e[0][0]['code'] == 34:
                return "Could not find user."
            else:
                return u"Error {}: {}".format(e[0][0]['code'], e[0][0]['message'])

        # get the users tweets
        user_timeline = api.user_timeline(id=user.id, count=tweet_number + 1)

        # if the timeline is empty, return an error
        if not user_timeline:
            return u"The user \x02{}\x02 has no tweets.".format(user.screen_name)

        # grab the newest tweet from the users timeline
        try:
            tweet = user_timeline[tweet_number]
        except IndexError:
            tweet_count = len(user_timeline)
            return u"The user \x02{}\x02 only has \x02{}\x02 tweets.".format(user.screen_name, tweet_count)

    elif re.match(r'^#\w+$', inp):
        # user is searching by hashtag
        search = api.search(inp)

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
        prefix = u"\u2713"
    else:
        prefix = ""

    time = timesince.timesince(tweet.created_at, datetime.utcnow())

    return u"{}@\x02{}\x02 ({}): {} ({} ago)".format(prefix, user.screen_name, user.name, text, time)


@hook.command("twinfo")
@hook.command
def twuser(inp, bot=None):
    """twuser <user> -- Get info on the Twitter user <user>"""

    api = get_api(bot)
    if not api:
        return "Error: No Twitter API details."

    try:
        # try to get user by username
        user = api.get_user(inp)
    except tweepy.error.TweepError as e:
        if e[0][0]['code'] == 34:
            return "Could not find user."
        else:
            return "Unknown error"

    if user.verified:
        prefix = u"\u2713"
    else:
        prefix = ""

    if user.location:
        loc_str = u" is located in \x02{}\x02 and".format(user.location)
    else:
        loc_str = ""

    if user.description:
        desc_str = u" The users description is \"{}\"".format(user.description)
    else:
        desc_str = ""

    return u"{}@\x02{}\x02 ({}){} has \x02{:,}\x02 tweets and \x02{:,}\x02 followers.{}" \
           "".format(prefix, user.screen_name, user.name, loc_str, user.statuses_count, user.followers_count,
                     desc_str)
