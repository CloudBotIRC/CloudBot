import requests

from cloudbot.util import web
from cloudbot import hook

api_url = "https://translate.yandex.net/api/v1.5/tr.json/"

@hook.on_start()
def load_key(bot):
    global api_key, lang_dict, lang_dir
    api_key = bot.config.get("api_keys", {}).get("yandex_translate", None)
    url = api_url + "getLangs"
    params = {
        'key':api_key,
        'ui':'en'
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return
    data = r.json()
    lang_dict = dict((v, k) for k, v in data['langs'].items())
    lang_dir = data['dirs']

def check_code(code):
    """checks the return code for the calls to yandex"""
    codes = {
        401: 'Invalid API key.',
        402: 'This API key has been blocked',
        403: 'The daily limit for requests has been reached',
        404: 'The daily limit of translated text has been reached',
        413: 'The text exceeds the maximum',
        422: 'The text could not be translated',
        501: 'The specified translation direction is not supported'
    }
    out = ""
    try:
        out = codes[code]
    except:
        out = "The API returned an undocumented error."
    return out

@hook.command("langlist", "tlist", autohelp=False)
def list_langs(message):
    """List the languages/codes that can be used to translate. Translation is powered by Yandex https://translate.yandex.com"""
    url = api_url + "getLangs"
    params = {
        'key':api_key,
        'ui':'en'
    }
    r = requests.get(url, params=params)
    data = r.json()
    langs = data['langs']
    out = "Language Codes:"
    out += ",".join("\n{}-{}".format(key, value) for (key, value) in sorted(langs.items(), ))
    out += "\n\nTranslation directions:"
    out += ",".join("\n{}".format(code) for code in data['dirs'])
    paste = web.paste(out, ext="txt")
    return "Here is information on what I can translate as well as valid language codes. {}".format(paste)

@hook.command("tran", "translate")
def trans(text):
    """tran <language or language code> text to translate. Translation is Powered by Yandex https://translate.yandex.com"""
    inp = text.split(' ',1)
    lang = inp[0].replace(':','')
    text = inp[1]
    if lang.title() in lang_dict.keys():
        lang = lang_dict[lang.title()]
    elif lang not in lang_dict.values() and lang not in lang_dir:
        return "Please specify a valid language, language code, to translate to. Use .langlist for more information on language codes and valid translation directions."
    url = api_url + "translate"
    params = {
        'key':api_key,
        'lang':lang,
        'text':text,
        'options':1
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return check_code(r.status_code)
    data = r.json()
    out = "Translation ({}): {}".format(data['lang'], data['text'][0])
    return out
