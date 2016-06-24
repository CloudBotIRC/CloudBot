import requests
import re

from cloudbot import hook

remove_html = re.compile("<.*?>")

@hook.command("bible", "passage", singlethreaded=True)
def bible(text):
    """Prints the specified passage from the Bible"""
    passage = text.strip()
    r = requests.get("https://labs.bible.org/api/?passage=" + passage)
    response = str(r.content, "utf-8")
    if not response.startswith("<b>"):
        return "Please enter a valid passage!"
    else:
        clean_text = re.sub(remove_html, "", response)
        return clean_text

