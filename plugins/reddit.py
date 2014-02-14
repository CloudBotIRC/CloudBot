from datetime import datetime
import re
import random

from util import hook, http, text, timesince


reddit_re = (r'.*(((www\.)?reddit\.com/r|redd\.it)[^ ]+)', re.I)

base_url = "http://reddit.com/r/{}/.json"
short_url = "http://redd.it/{}"


@hook.regex(*reddit_re)
def reddit_url(match):
    thread = http.get_html(match.group(0))

    title = thread.xpath('//title/text()')[0]
    upvotes = thread.xpath("//span[@class='upvotes']/span[@class='number']/text()")[0]
    downvotes = thread.xpath("//span[@class='downvotes']/span[@class='number']/text()")[0]
    author = thread.xpath("//div[@id='siteTable']//a[contains(@class,'author')]/text()")[0]
    timeago = thread.xpath("//div[@id='siteTable']//p[@class='tagline']/time/text()")[0]
    comments = thread.xpath("//div[@id='siteTable']//a[@class='comments']/text()")[0]

    return u'\x02{}\x02 - posted by \x02{}\x02 {} ago - {} upvotes, {} downvotes - {}'.format(
        title, author, timeago, upvotes, downvotes, comments)


@hook.command(autohelp=False)
def reddit(inp):
    """reddit <subreddit> [n] -- Gets a random post from <subreddit>, or gets the [n]th post in the subreddit."""
    id_num = None

    if inp:
        # clean and split the input
        parts = inp.lower().strip().split()

        # find the requested post number (if any)
        if len(parts) > 1:
            url = base_url.format(parts[0].strip())
            try:
                id_num = int(parts[1]) - 1
            except ValueError:
                return "Invalid post number."
        else:
            url = base_url.format(parts[0].strip())
    else:
        url = "http://reddit.com/.json"

    try:
        data = http.get_json(url, user_agent=http.ua_chrome)
    except Exception as e:
        return "Error: " + str(e)
    data = data["data"]["children"]

    # get the requested/random post
    if id_num is not None:
        try:
            item = data[id_num]["data"]
        except IndexError:
            length = len(data)
            return "Invalid post number. Number must be between 1 and {}.".format(length)
    else:
        item = random.choice(data)["data"]

    item["title"] = text.truncate_str(item["title"], 50)
    item["link"] = short_url.format(item["id"])

    raw_time = datetime.fromtimestamp(int(item["created_utc"]))
    item["timesince"] = timesince.timesince(raw_time)

    if item["over_18"]:
        item["warning"] = " \x02NSFW\x02"
    else:
        item["warning"] = ""

    return u"\x02{title} : {subreddit}\x02 - posted by \x02{author}\x02" \
           " {timesince} ago - {ups} upvotes, {downs} downvotes -" \
           " {link}{warning}".format(**item)
