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

def smart_truncate(content, length=425, suffix='...\n'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' ', 1)[0]+ suffix + content[:length].rsplit(' ', 1)[1] + smart_truncate(content[length:])


@hook.command("quran", "verse", singlethreaded=True)
def quran(text, message):
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
    message(out)
    translation = smart_truncate(data2['Text'])
    return translation
