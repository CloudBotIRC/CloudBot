# Gets an imgur link from /r/aww
from util import hook, http
import random


@hook.command
def aww(inp):
    try:
        data = http.get_json("http://reddit.com/r/aww/.json",
                             user_agent=http.ua_chrome)
    except Exception as e:
        return "Error: " + str(e)
    data = data["data"]["children"]
    item = None
    while not item:
        tempitem = random.choice(data)
        if tempitem["data"]["domain"] == "i.imgur.com":
            item = tempitem["data"]
    return "%s %s" % (item["title"], item["url"])
