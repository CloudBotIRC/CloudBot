import json
import os
import random

from cloudbot.util import web
from cloudbot import hook

@hook.onload()
def load_drinks(bot):
    """load the drink recipes"""
    global drinks
    with open(os.path.join(bot.data_dir, "drinks.json")) as json_data:
        drinks = json.load(json_data)


@hook.command()
def drink(text, chan, action):
    """<nick>, makes the user a random cocktail."""
    index = random.randint(0,len(drinks)-1)
    drink = drinks[index]['title']
    url = web.try_shorten(drinks[index]['url'])
    if drink.endswith(' recipe'):
        drink = drink[:-7]
    contents = drinks[index]['ingredients']
    directions = drinks[index]['directions']
    out = "grabs some"
    for x in contents:
        if x == contents[len(contents)-1]:
            out += " and {}".format(x)
        else:
            out += " {},".format(x)
    out += "\x0F and makes {} a(n) \x02{}\x02. {}".format(text, drink, url)
    action(out, chan)

