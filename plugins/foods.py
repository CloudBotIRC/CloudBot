import asyncio
import codecs
import json
import os
import random
import re

from cloudbot import hook
from cloudbot.util import textgen

nick_re = re.compile("^[A-Za-z0-9_|.\-\]\[\{\}]*$", re.I)

biscuits = ['Digestive', 'Chocolate Digestive', 'Caramel Digestive', 'Hobnob', 'Chocolate Hobnob', 'Rich Tea Finger',
            'Rich Tea', 'Custard Cream', 'Chocolate Finger', 'Ginger Nut', 'Penguin Bar', 'Fruit Shortcake',
            'Caramel Wafer', 'Shortbread Round', 'Lemon Puff', 'Elite Chocolate Tea Cake', 'Club Bar', 'Garbaldi',
            'Viennese', 'Bourbon Cream', 'Malted Milk', 'Lotus Biscoff', 'Nice', 'Fig Roll', 'Jammie Dodger', 'Oatie',
            'Jaffa Cake']


# <Luke> Hey guys, any good ideas for plugins?
# <User> I don't know, something that lists every potato known to man?
# <Luke> BRILLIANT


def is_valid(target):
    """ Checks if a string is a valid IRC nick. """
    if nick_re.match(target):
        return True
    else:
        return False


@hook.on_start()
def load_foods(bot):
    """
    :type bot: cloudbot.bot.CloudBot
    """
    global sandwich_data, taco_data, burrito_data, potato_data, cake_data, cookie_data, biscuit_data

    with codecs.open(os.path.join(bot.data_dir, "sandwich.json"), encoding="utf-8") as f:
        sandwich_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "taco.json"), encoding="utf-8") as f:
        taco_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "potato.json"), encoding="utf-8") as f:
        potato_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "burrito.json"), encoding="utf-8") as f:
        burrito_data = json.load(f)
    with codecs.open(os.path.join(bot.data_dir, "cake.json"), encoding="utf-8") as f:
        cake_data = json.load(f)
    with codecs.open(os.path.join(bot.data_dir, "cookie.json"), encoding="utf-8") as f:
        cookie_data = json.load(f)


@asyncio.coroutine
@hook.command
def potato(text, action):
    """<user> - makes <user> a tasty little potato"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give a potato to that user."

    generator = textgen.TextGenerator(potato_data["templates"], potato_data["parts"], variables={"user": user})
    action(generator.generate_string())


@asyncio.coroutine
@hook.command
def cake(text, action):
    """<user> - gives <user> an awesome cake"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give a cake to that user."

    generator = textgen.TextGenerator(cake_data["templates"], cake_data["parts"], variables={"user": user})
    action(generator.generate_string())


@asyncio.coroutine
@hook.command
def cookie(text, action):
    """<user> - gives <user> a cookie"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give a cookie to that user."

    generator = textgen.TextGenerator(cookie_data["templates"], cookie_data["parts"], variables={"user": user})
    action(generator.generate_string())


@asyncio.coroutine
@hook.command
def biscuit(text, action):
    """<user> - gives <user> a biscuit"""
    user = text.strip()
    name = random.choice(['bickie', 'biscuit'])
    flavor = random.choice(['tasty', 'delectable', 'delicious', 'yummy', 'gorgeous', 'scrumptious', 'luscious',
                            'irresistible', 'mouth watering'])
    if not is_valid(user):
        return "I can't give a {} {} to that user.".format(flavor, name)

    bickie_type = random.choice(biscuits)
    method = random.choice(['makes', 'gives', 'gets', 'buys', 'unwantingly passes', 'grants', 'force feeds'])

    action("{} {} a {} {} {}!".format(method, user, flavor, bickie_type, name))


@asyncio.coroutine
@hook.command
def sandwich(text, action):
    """<user> - gives a tasty sandwich to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give a sandwich to that user."

    generator = textgen.TextGenerator(sandwich_data["templates"], sandwich_data["parts"],
                                      variables={"user": user})

    # act out the message
    action(generator.generate_string())


@asyncio.coroutine
@hook.command
def taco(text, action):
    """<user> - gives a taco to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give a taco to that user."

    generator = textgen.TextGenerator(taco_data["templates"], taco_data["parts"],
                                      variables={"user": user})

    # act out the message
    action(generator.generate_string())


@asyncio.coroutine
@hook.command
def burrito(text, action):
    """<user> - gives a burrito to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give a burrito to that user."

    generator = textgen.TextGenerator(burrito_data["templates"], burrito_data["parts"],
                                      variables={"user": user})

    action(generator.generate_string())
