
from util import hook, http, text, timesince
import re
import random
from pprint import pprint


reddit_url = "http://redd.it/{}"
base_url = "http://reddit.com/r/{}/.json"
imgur_re = re.compile(r'http://(?:i\.)?imgur\.com/(?:(a)(?:/(\w+))?|(\w+\b(?!/))\.?\w?)')

image_api = "https://api.imgur.com/3/image/{}.json"
album_api = "https://api.imgur.com/3/album/{}.json"

def imgur_query(image_id, is_album=False):
    if is_album:
        url = album_api.format(image_id)
    else:
        url = image_api.format(image_id)
    return http.get_json(url)


def is_valid(data):
    if data["domain"] in ["i.imgur.com", "imgur.com"]:
        return True
    else:
        return False


@hook.command
def imgur(inp):
    try:
        data = http.get_json(base_url.format(inp.strip()),
                             user_agent=http.ua_chrome)
    except Exception as e:
        return "Error: " + str(e)

    data = data["data"]["children"]
    random.shuffle(data)

    # filter list to only have 10 imgur links
    filtered_list = [i["data"] for i in data if is_valid(i["data"])][:10]

    if not filtered_list:
        return "No images found."

    items = []

    headers = {
    "Authorization": "Client-ID b5d127e6941b07a"
    }

    for item in filtered_list:
        match = imgur_re.search(item["url"])
        if match.group(1) == 'a':
            url = album_api.format(match.group(2))
            is_album = True
        elif match.group(3) is not None:
            url = image_api.format(match.group(3))
            is_album = False

        result = http.get_json(url, headers=headers)["data"]

        if is_album:
            items.append(result["id"])
        else:
            items.append(result["id"])

    #post_data = {
    #    "ids": items,
    #    "title": "images from /r/{}/".format(inp)
    #}

    #album = http.get("https://api.imgur.com/3/album/",  post_data=post_data, get_method="post", headers=headers)
    #pprint(album)



    return "http://imgur.com/" + ','.join(items)

