import re
import random

import requests
import urllib.parse

from cloudbot import hook
from cloudbot.util import web


API_URL = 'http://api.wordnik.com/v4/'
WEB_URL = 'https://www.wordnik.com/words/{}'

ATTRIB_NAMES = {
    'ahd-legacy': 'AHD/Wordnik',
    'century': 'Century/Wordnik',
    'wiktionary': 'Wiktionary/Wordnik',
    'gcide': 'GCIDE/Wordnik',
    'wordnet': 'Wordnet/Wordnik'
}

def sanitize(text):
    return urllib.parse.quote(text.translate({ord('\\'):None, ord('/'):None}))

@hook.on_start()
def load_key(bot):
    global api_key
    api_key = bot.config.get("api_keys", {}).get("wordnik", None)


@hook.command("define", "dictionary")
def define(text):
    """<word> -- Returns a dictionary definition from Wordnik for <word>."""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    word = sanitize(text)
    url = API_URL + "word.json/{}/definitions".format(word)

    params = {
        'api_key': api_key,
        'limit': 1
    }
    json = requests.get(url, params=params).json()

    if json:
        data = json[0]
        data['word'] = " ".join(data['word'].split())
        data['url'] = web.try_shorten(WEB_URL.format(data['word']))
        data['attrib'] = ATTRIB_NAMES[data['sourceDictionary']]
        return "\x02{word}\x02: {text} - {url} ({attrib})".format(**data)
    else:
        return "I could not find a definition for \x02{}\x02.".format(word)


@hook.command("wordusage", "wordexample", "usage")
def word_usage(text):
    """<word> -- Returns an example sentence showing the usage of <word>."""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    word = sanitize(text)
    url = API_URL + "word.json/{}/examples".format(word)
    params = {
        'api_key': api_key,
        'limit': 10
    }

    json = requests.get(url, params=params).json()
    if json:
        out = "\x02{}\x02: ".format(word)
        example = random.choice(json['examples'])
        out += "{} ".format(example['text'])
        return " ".join(out.split())
    else:
        return "I could not find any usage examples for \x02{}\x02.".format(word)


@hook.command("pronounce", "sounditout")
def pronounce(text):
    """<word> -- Returns instructions on how to pronounce <word> with an audio example."""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    word = sanitize(text)
    url = API_URL + "word.json/{}/pronunciations".format(word)

    params = {
        'api_key': api_key,
        'limit': 5
    }
    json = requests.get(url, params=params).json()

    if json:
        out = "\x02{}\x02: ".format(word)
        out += " • ".join([i['raw'] for i in json])
    else:
        return "Sorry, I don't know how to pronounce \x02{}\x02.".format(word)

    url = API_URL + "word.json/{}/audio".format(word)

    params = {
        'api_key': api_key,
        'limit': 1,
        'useCanonical': 'false'
    }
    json = requests.get(url, params=params).json()

    if json:
        url = web.try_shorten(json[0]['fileUrl'])
        out += " - {}".format(url)

    return " ".join(out.split())


@hook.command()
def synonym(text):
    """<word> -- Returns a list of synonyms for <word>."""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    word = sanitize(text)
    url = API_URL + "word.json/{}/relatedWords".format(word)

    params = {
        'api_key': api_key,
        'relationshipTypes': 'synonym',
        'limitPerRelationshipType': 5
    }
    json = requests.get(url, params=params).json()

    if json:
        out = "\x02{}\x02: ".format(word)
        out += " • ".join(json[0]['words'])
        return " ".join(out.split())
    else:
        return "Sorry, I couldn't find any synonyms for \x02{}\x02.".format(word)


@hook.command()
def antonym(text):
    """<word> -- Returns a list of antonyms for <word>."""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    word = sanitize(text)
    url = API_URL + "word.json/{}/relatedWords".format(word)

    params = {
        'api_key': api_key,
        'relationshipTypes': 'antonym',
        'limitPerRelationshipType': 5,
        'useCanonical': 'false'
    }
    json = requests.get(url, params=params).json()

    if json:
        out = "\x02{}\x02: ".format(word)
        out += " • ".join(json[0]['words'])
        out = out[:-2]
        return " ".join(out.split())
    else:
        return "Sorry, I couldn't find any antonyms for \x02{}\x02.".format(word)


# word of the day
@hook.command("word", "wordoftheday", autohelp=False)
def wordoftheday(text):
    """returns the word of the day. To see past word of the day enter use the format yyyy-MM-dd. The specified date must be after 2009-08-10."""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    match = re.search(r'(\d\d\d\d-\d\d-\d\d)', text)
    date = ""
    if match:
        date = match.group(1)
    url = API_URL + "words.json/wordOfTheDay"
    if date:
        params = {
            'api_key': api_key,
            'date': date
        }
        day = date
    else:
        params = {
            'api_key': api_key,
        }
        day = "today"

    json = requests.get(url, params=params).json()

    if json:
        word = json['word']
        note = json['note']
        pos = json['definitions'][0]['partOfSpeech']
        definition = json['definitions'][0]['text']
        out = "The word for \x02{}\x02 is \x02{}\x02: ".format(day, word)
        out += "\x0305({})\x0305 ".format(pos)
        out += "\x0310{}\x0310 ".format(note)
        out += "\x02Definition:\x02 \x0303{}\x0303".format(definition)
        return " ".join(out.split())
    else:
        return "Sorry I couldn't find the word of the day, check out this awesome otter instead {}".format(
            "http://i.imgur.com/pkuWlWx.gif")


# random word
@hook.command("wordrandom", "randomword", autohelp=False)
def random_word():
    """Grabs a random word from wordnik.com"""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    url = API_URL + "words.json/randomWord"
    params = {
        'api_key': api_key,
        'hasDictionarydef': 'true',
        'vulgar': 'true'
    }
    json = requests.get(url, params=params).json()
    if json:
        word = json['word']
        return "Your random word is \x02{}\x02.".format(word)
    else:
        return "There was a problem contacting the Wordnik API."
