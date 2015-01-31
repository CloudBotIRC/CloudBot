import re
import random

from imgurpython import ImgurClient
from contextlib import suppress

from cloudbot import hook
from cloudbot.util import web


# imgurpython has an issue where it does not allow anonymous album creation
# to fix this we monkeypatch logged_in to disable login checking
# yes, it's kinda dirty, but it works :)
ImgurClient.logged_in = lambda x: None

NO_NSFW = False


def get_items(text):
    if text:
        reddit_search = re.search(r"/r/([^\s/]+)", text)
        user_search = re.search(r"/user/([^\s/]+)", text)

        if reddit_search:
            subreddit = reddit_search.groups()[0]
            items = imgur_api.subreddit_gallery(subreddit)
        elif user_search:
            user = user_search.groups()[0]
            items = imgur_api.get_account_submissions(user)
        elif text in ("meme", "memes"):
            items = imgur_api.memes_subgallery()
        elif text == "random":
            page = random.randint(1, 50)
            items = imgur_api.gallery_random(page=page)
        else:
            page = random.randint(1, 5)
            items = imgur_api.gallery_search(text, page=page)
    else:
        reddit_search = False
        items = imgur_api.gallery()

    if NO_NSFW:
        items = [item for item in items if not item.nsfw]

    return items, reddit_search


@hook.on_start()
def load_api(bot):
    global imgur_api

    client_id = bot.config.get("api_keys", {}).get("imgur_client_id")
    client_secret = bot.config.get("api_keys", {}).get("imgur_client_secret")

    if None in (client_id, client_secret):
        imgur_api = None
        return
    else:
        imgur_api = ImgurClient(client_id, client_secret)


@hook.command(autohelp=False)
def imgur(text):
    """[search term] / [/r/subreddit] / [/user/username] / memes / random - returns a link to a random imgur image based
     on your input. if no input is given the bot will get an image from the imgur frontpage """
    text = text.strip().lower()

    if not imgur_api:
        return "No imgur API details"

    if text == "apicredits":
        return imgur_api.credits

    items, is_reddit = get_items(text)

    if not items:
        return "No results found."

    # if the item has no title, we don't want it. ugh >_>
    items = [item for item in items if item.title]

    random.shuffle(items)
    item = random.choice(items)

    tags = []

    # remove unslightly full stops
    if item.title.endswith("."):
        title = item.title[:-1]
    else:
        title = item.title

    # if it's an imgur meme, add the meme name
    # if not, AttributeError will trigger and code will carry on
    with suppress(AttributeError):
        title = "\x02{}\x02 - {}".format(item.meme_metadata["meme_name"].lower(), title)

    # if the item has a tag, show that
    if item.section:
        tags.append(item.section)

    # if the item is nsfw, show that
    if item.nsfw:
        tags.append("nsfw")

    # if the search was a subreddit search, add the reddit comment link
    if is_reddit:
        reddit_url = web.try_shorten("http://reddit.com" + item.reddit_comments)
        url = "{} ({})".format(item.link, reddit_url)
    else:
        url = "{}".format(item.link)

    tag_str = "[\x02" + ("\x02, \x02".join(tags)) + "\x02] " if tags else ""

    return '{}"{}" - {}'.format(tag_str, title, url)


@hook.command("imguralbum", "multiimgur", "imgalbum", "album", autohelp=False)
def imguralbum(text, conn):
    """[search term] / [/r/subreddit] / [/user/username] / memes / random - returns a link to lots of random images
    based on your input. if no input is given the bot will get images from the imgur frontpage """
    text = text.strip().lower()

    if not imgur_api:
        return "No imgur API details"

    if text == "apicredits":
        return imgur_api.credits

    items, is_reddit = get_items(text)

    if not items:
        return "No results found."

    random.shuffle(items)
    items = items[:50]

    nsfw = any([item.nsfw for item in items])

    params = {
        'title': '{} presents: "{}"'.format(conn.nick, text or "random images"),
        'ids': ",".join([item.id for item in items]),
        'layout': 'blog',
        'account_url': None
    }
    album = imgur_api.create_album(params)

    if nsfw:
        return "[\x02nsfw\x02] https://imgur.com/a/" + album["id"]
    else:
        return "https://imgur.com/a/" + album["id"]
