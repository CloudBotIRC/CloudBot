import requests
import re

from cloudbot import hook

@hook.command("bible", "passage", singlethreaded=True)
def bible(text):
    """Prints the specified passage from the Bible"""
    passage = text.strip()
    params = {
        'passage':passage,
        'formatting':'plain',
        'type':'json'
    }
    r = requests.get("https://labs.bible.org/api", params=params)
    try:
        response = r.json()[0]
    except:
        return "Something went wrong, either you entered an invalid passage or the API is down."
    book = response['bookname']
    ch = response['chapter']
    ver = response['verse']
    txt = response['text']
    return "\x02{} {}:{}\x02 {}".format(book, ch, ver, txt)
