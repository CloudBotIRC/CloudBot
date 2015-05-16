import requests

from cloudbot import hook

def statuscheck(status, item):
    """since we are doing this a lot might as well return something more meaningful"""
    out = ""
    if status == 404:
        out = "It appears {} does not exist.".format(item)
    elif status == 503:
        out = "Qur'an API is having problems, it would be best to check back later."
    else:
        out = "Qur'an API returned an error, response: {}".format(status)
    return out

@hook.command("quran", "verse", singlethreaded=True)
def quran(text):
    """Prints the specified Qur'anic verse(s) and its/their translation(s)"""
    api_url = "http://quranapi.azurewebsites.net/api/verse/"
    chapter = text.split(':')[0]
    verse = text.split(':')[1]
    params={"chapter":chapter, "number": verse, "lang": "ar"}
    r = requests.get(api_url, params=params)
    if r.status_code != 200:
        return statuscheck(r.status_code, text)
    params["lang"] = "en"
    r2 = requests.get(api_url, params=params)
    data = r.json()
    data2 = r2.json()
    out = "\x02{}\x02: ".format(text)
    verse = data['Text']
    out += verse
    translation = data2['Text']
    out += " \u2022 {}".format(translation)
    return out
