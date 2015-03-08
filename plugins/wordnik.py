import requests
import re
import random

from cloudbot import hook
from cloudbot.util import web

base_url = 'http://api.wordnik.com/v4/'

@hook.on_start()
def load_key(bot):
    global api_key
    api_key = bot.config.get("api_keys", {}).get("wordnik", None)


# word usage
@hook.command("wordexample", "wordusage", "usage")
def wordexample(text, conn):
    """Provides an example sentance of the usage of a specified word."""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    word = text.split(' ')[0]
    url = base_url + "word.json/{}/examples".format(word)
    params = {
        'api_key': api_key,
        'limit': 10
    }

    json = requests.get(url, params=params).json()
    if json:
        out = "\x02{}\x02: ".format(word)
        i = random.randint(0, len(json['examples']) - 1)
        out += "{} ".format(json['examples'][i]['text'])
        return out
    else:
        return "I could not find any usage examples for the word: {}".format(word)

# word definitions


@hook.command("define", "dictionary")
def define(text, conn):
    """Returns a definition for the given word."""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    word = text.split(' ')[0]
    url = base_url + "word.json/{}/definitions".format(word)
    dictionaries = {
        'ahd-legacy': 'The American Heritage Dictionary',
        'century': 'The Century Dictionary',
        'wiktionary': 'Wiktionary',
        'gcide': 'Collaborative International Dictionary of English',                     'wordnet': 'Wordnet 3.0'
    }

    params = {
        'api_key': api_key,
        'limit': 1
    }
    json = requests.get(url, params=params).json()

    if json:
        out = "\x02{}\x02: ".format(word)
        out += "{} From {}.".format(json[0]['text'],
                                    dictionaries[json[0]['sourceDictionary']])
        return out
    else:
        return "I could not find a definition for {}.".format(word)

# word pronunciations


@hook.command("pronounce", "sounditout")
def prounounce(text, conn):
    """Input a word and I will tell you how to pronounce it."""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    word = text.split(' ')[0]
    url = base_url + "word.json/{}/pronunciations".format(word)

    params = {
        'api_key': api_key,
        'limit': 5
    }
    json = requests.get(url, params=params).json()

    if json:
        out = "\x02{}\x02: ".format(word)
        for i in range(len(json)):
            out += "{} {} ".format(json[i]['raw'], u'\u2022')
        out = out[:-3] + ". "
        out += word_audio(word, conn)
        return out
    else:
        return "Sorry I don't know how to pronounce {} either.".format(word)


# synonym
@hook.command()
def synonym(text, conn):
    """provides a list of synonyms for a given word"""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    word = text.split(' ')[0]
    url = base_url + "word.json/{}/relatedWords".format(word)

    params = {
        'api_key': api_key,
        'relationshipTypes': 'synonym',
        'limitPerRelationshipType': 5
    }
    json = requests.get(url, params=params).json()

    if json:
        out = "\x02{}\x02: ".format(word)
        for i in range(len(json[0]['words'])):
            out += "{} {} ".format(json[0]['words'][i], u'\u2022')
        out = out[:-2]
        return out
    else:
        return "Sorry, I couldn't find any synonyms for {}.".format(word)


# antonym
@hook.command()
def antonym(text, conn):
    """provides a list of antonyms for a given word"""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    word = text.split(' ')[0]
    url = base_url + "word.json/{}/relatedWords".format(word)

    params = {
        'api_key': api_key,
        'relationshipTypes': 'antonym',
        'limitPerRelationshipType': 5,
        'useCanonical': 'false'
    }
    json = requests.get(url, params=params).json()

    if json:
        out = "\x02{}\x02: ".format(word)
        for i in range(len(json[0]['words'])):
            out += "{} {} ".format(json[0]['words'][i], u'\u2022')
        out = out[:-2]
        return out
    else:
        return "Sorry, I couldn't find any antonyms for {}.".format(word)


# audio pronunciation
@hook.command("wordaudio", "audioword")
def word_audio(text, conn):
    """provides a link to the audible pronunciation of a given word"""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    word = text.split(' ')[0]
    url = base_url + "word.json/{}/audio".format(word)

    params = {
        'api_key': api_key,
        'limit': 1,
        'useCanonical': 'false'
    }
    json = requests.get(url, params=params).json()

    if json:
        out = "This is how you say \x02{}\x02: ".format(word)
        audio = web.try_shorten(json[0]['fileUrl'])
        out += "{}".format(audio)
        return out
    else:
        return "Sorry, I couldn't find an audio pronunciation for {}.".format(word)


# word of the day
@hook.command("word", "wordoftheday", autohelp=False)
def wordoftheday(text, conn):
    """returns the word of the day. To see past word of the day enter use the format yyyy-MM-dd. The specified date must be after 2009-08-10."""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    match = re.search(r'(\d\d\d\d-\d\d-\d\d)', text)
    date = ""
    if match:
        date = match.group(1)
    url = base_url + "words.json/wordOfTheDay"
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
        return out
    else:
        return "Sorry I couldn't find the word of the day, check out this awesome otter instead {}".format("http://i.imgur.com/pkuWlWx.gif")


# random word
@hook.command("wordrandom", "randomword", autohelp=False)
def random_word(conn):
    """Grabs a random word from wordnik.com"""
    if not api_key:
        return "This command requires an API key from wordnik.com."
    url = base_url + "words.json/randomWord"
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
        return "There was a problem contacting the wordnick.com API."
