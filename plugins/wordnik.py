import requests
import random

from cloudbot import hook
from cloudbot.util import formatting, web

base_url = 'http://api.wordnik.com/v4/'


@hook.on_start()
def load_key(bot):
    global api_key
    api_key = bot.config.get("api_keys", {}).get("wordnik", None)


# word usage
@hook.command("wordexample", "wordusage")
def wordexample(text, conn):
    """Provides an example sentance of the usage of a specified word."""
    word = text.split(' ')[0]
    url = base_url
    url += "word.json/{}/examples".format(word)
    params = {
               'api_key': api_key,
               'limit':10
             }
 
    json = requests.get(url, params=params).json()
    if json:
        out = "Usage for the word {}: ".format(word)
        i = random.randint(0,len(json['examples'])-1)
        out += "{} ".format(json['examples'][i]['text'])
        return out
    else:
        return "I could not find any usage examples for the word: {}".format(word)

# word definitions
@hook.command("define", "dictionary")
def define(text, conn):
    """Returns a definition for the given word."""
    word = text.split(' ')[0]
    url = base_url
    url += "word.json/{}/definitions".format(word)
    dictionaries = {
                     'ahd-legacy': 'The American Heritage Dictionary',
                     'century': 'The Century Dictionary',
                     'wiktionary':'Wiktionary',
                     'gcide':'Collaborative International Dictionary of English',                     'wordnet':'Wordnet 3.0'
                    }

    params = {
               'api_key': api_key,
               'limit': 1
             }
    json = requests.get(url, params=params).json()
   
    if json:
        out = "{} defined: ".format(word)
        out += "{} From {}".format(json[0]['text'], dictionaries[json[0]['sourceDictionary']])
        return out
    else:
        return "I could find a definition for {}.".format(word)

# word pronunciations




# synonym



# antonym



# pronunciation




# audio pronunciation



# word of the day


# random word




