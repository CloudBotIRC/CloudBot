import asyncio
import json

import codecs
import os
import random
import re

from cloudbot import hook
from cloudbot.util import textgen

nick_re = re.compile("^[A-Za-z0-9_|.\-\]\[\{\}]*$", re.I)

cakes = ['Chocolate', 'Ice Cream', 'Angel', 'Boston Cream', 'Birthday', 'Bundt', 'Carrot', 'Coffee', 'Devils', 'Fruit',
         'Gingerbread', 'Pound', 'Red Velvet', 'Stack', 'Welsh', 'Yokan']

cookies = ['Chocolate Chip', 'Oatmeal', 'Sugar', 'Oatmeal Raisin', 'Macadamia Nut', 'Jam Thumbprint', 'Medican Wedding',
           'Biscotti', 'Oatmeal Cranberry', 'Chocolate Fudge', 'Peanut Butter', 'Pumpkin', 'Lemon Bar',
           'Chocolate Oatmeal Fudge', 'Toffee Peanut', 'Danish Sugar', 'Triple Chocolate', 'Oreo']

biscuits = ['Digestive', 'Chocolate Digestive', 'Caramel Digestive', 'Hobnob', 'Chocolate Hobnob', 'Rich Tea Finger',
            'Rich Tea', 'Custard Cream', 'Chocolate Finger', 'Ginger Nut', 'Penguin Bar', 'Fruit Shortcake',
            'Caramel Wafer', 'Shortbread Round', 'Lemon Puff', 'Elite Chocolate Tea Cake', 'Club Bar', 'Garbaldi',
            'Viennese', 'Bourbon Cream', 'Malted Milk', 'Lotus Biscoff', 'Nice', 'Fig Roll', 'Jammie Dodger', 'Oatie',
            'Jaffa Cake']

# <Luke> Hey guys, any good ideas for plugins?
# <User> I don't know, something that lists every potato known to man?
# <Luke> BRILLIANT
potatoes = ['AC Belmont', 'AC Blue Pride', 'AC Brador', 'AC Chaleur', 'AC Domino', 'AC Dubuc', 'AC Glacier Chip',
            'AC Maple Gold', 'AC Novachip', 'AC Peregrine Red', 'AC Ptarmigan', 'AC Red Island', 'AC Saguenor',
            'AC Stampede Russet', 'AC Sunbury', 'Abeille', 'Abnaki', 'Acadia', 'Acadia Russet', 'Accent',
            'Adirondack Blue', 'Adirondack Red', 'Adora', 'Agria', 'All Blue', 'All Red', 'Alpha', 'Alta Russet',
            'Alturas Russet', 'Amandine', 'Amisk', 'Andover', 'Anoka', 'Anson', 'Aquilon', 'Arran Consul', 'Asterix',
            'Atlantic', 'Austrian Crescent', 'Avalanche', 'Banana', 'Bannock Russet', 'Batoche', 'BeRus',
            'Belle De Fonteney', 'Belleisle', 'Bintje', 'Blossom', 'Blue Christie', 'Blue Mac', 'Brigus',
            'Brise du Nord', 'Butte', 'Butterfinger', 'Caesar', 'CalWhite', 'CalRed', 'Caribe', 'Carlingford',
            'Carlton', 'Carola', 'Cascade', 'Castile', 'Centennial Russet', 'Century Russet', 'Charlotte', 'Cherie',
            'Cherokee', 'Cherry Red', 'Chieftain', 'Chipeta', 'Coastal Russet', 'Colorado Rose', 'Concurrent',
            'Conestoga', 'Cowhorn', 'Crestone Russet', 'Crispin', 'Cupids', 'Daisy Gold', 'Dakota Pearl', 'Defender',
            'Delikat', 'Denali', 'Desiree', 'Divina', 'Dundrod', 'Durango Red', 'Early Rose', 'Elba', 'Envol',
            'Epicure', 'Eramosa', 'Estima', 'Eva', 'Fabula', 'Fambo', 'Fremont Russet', 'French Fingerling',
            'Frontier Russet', 'Fundy', 'Garnet Chile', 'Gem Russet', 'GemStar Russet', 'Gemchip', 'German Butterball',
            'Gigant', 'Goldrush', 'Granola', 'Green Mountain', 'Haida', 'Hertha', 'Hilite Russet', 'Huckleberry',
            'Hunter', 'Huron', 'IdaRose', 'Innovator', 'Irish Cobbler', 'Island Sunshine', 'Ivory Crisp',
            'Jacqueline Lee', 'Jemseg', 'Kanona', 'Katahdin', 'Kennebec', "Kerr's Pink", 'Keswick', 'Keuka Gold',
            'Keystone Russet', 'King Edward VII', 'Kipfel', 'Klamath Russet', 'Krantz', 'LaRatte', 'Lady Rosetta',
            'Latona', 'Lemhi Russet', 'Liberator', 'Lili', 'MaineChip', 'Marfona', 'Maris Bard', 'Maris Piper',
            'Matilda', 'Mazama', 'McIntyre', 'Michigan Purple', 'Millenium Russet', 'Mirton Pearl', 'Modoc', 'Mondial',
            'Monona', 'Morene', 'Morning Gold', 'Mouraska', 'Navan', 'Nicola', 'Nipigon', 'Niska', 'Nooksack',
            'NorValley', 'Norchip', 'Nordonna', 'Norgold Russet', 'Norking Russet', 'Norland', 'Norwis', 'Obelix',
            'Ozette', 'Peanut', 'Penta', 'Peribonka', 'Peruvian Purple', 'Pike', 'Pink Pearl', 'Prospect', 'Pungo',
            'Purple Majesty', 'Purple Viking', 'Ranger Russet', 'Reba', 'Red Cloud', 'Red Gold', 'Red La Soda',
            'Red Pontiac', 'Red Ruby', 'Red Thumb', 'Redsen', 'Rocket', 'Rose Finn Apple', 'Rose Gold', 'Roselys',
            'Rote Erstling', 'Ruby Crescent', 'Russet Burbank', 'Russet Legend', 'Russet Norkotah', 'Russet Nugget',
            'Russian Banana', 'Saginaw Gold', 'Sangre', 'Satina', 'Saxon', 'Sebago', 'Shepody', 'Sierra',
            'Silverton Russet', 'Simcoe', 'Snowden', 'Spunta', "St. John's", 'Summit Russet', 'Sunrise', 'Superior',
            'Symfonia', 'Tolaas', 'Trent', 'True Blue', 'Ulla', 'Umatilla Russet', 'Valisa', 'Van Gogh', 'Viking',
            'Wallowa Russet', 'Warba', 'Western Russet', 'White Rose', 'Willamette', 'Winema', 'Yellow Finn',
            'Yukon Gold']


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
    global sandwich_data, taco_data

    with codecs.open(os.path.join(bot.data_dir, "sandwich.json"), encoding="utf-8") as f:
        sandwich_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "taco.json"), encoding="utf-8") as f:
        taco_data = json.load(f)


@asyncio.coroutine
@hook.command
def potato(text, action):
    """<user> - makes <user> a tasty little potato"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give a potato to that user."

    potato_type = random.choice(potatoes)
    size = random.choice(['small', 'little', 'mid-sized', 'medium-sized', 'large', 'gigantic'])
    flavor = random.choice(['tasty', 'delectable', 'delicious', 'yummy', 'toothsome', 'scrumptious', 'luscious'])
    method = random.choice(['bakes', 'fries', 'boils', 'roasts'])
    side_dish = random.choice(['side salad', 'dollop of sour cream', 'piece of chicken', 'bowl of shredded bacon'])

    action("{} a {} {} {} potato for {} and serves it with a small {}!".format(method, flavor, size, potato_type, user,
                                                                               side_dish))


@asyncio.coroutine
@hook.command
def cake(text, action):
    """<user> - gives <user> an awesome cake"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give a cake to that user."

    cake_type = random.choice(cakes)
    size = random.choice(['small', 'little', 'mid-sized', 'medium-sized', 'large', 'gigantic'])
    flavor = random.choice(['tasty', 'delectable', 'delicious', 'yummy', 'toothsome', 'scrumptious', 'luscious'])
    method = random.choice(['makes', 'gives', 'gets', 'buys'])
    side_dish = random.choice(['glass of chocolate milk', 'bowl of ice cream', 'jar of cookies',
                               'some chocolate sauce'])

    action("{} {} a {} {} {} cake and serves it with a small {}!".format(method, user, flavor, size, cake_type,
                                                                         side_dish))


@asyncio.coroutine
@hook.command
def cookie(text, action):
    """<user> - gives <user> a cookie"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give a cookie to that user."

    cookie_type = random.choice(cookies)
    size = random.choice(['small', 'little', 'medium-sized', 'large', 'gigantic'])
    flavor = random.choice(['tasty', 'delectable', 'delicious', 'yummy', 'toothsome', 'scrumptious', 'luscious'])
    method = random.choice(['makes', 'gives', 'gets', 'buys'])
    side_dish = random.choice(['glass of milk', 'bowl of ice cream', 'bowl of chocolate sauce'])

    action("{} {} a {} {} {} cookie and serves it with a {}!".format(method, user, flavor, size, cookie_type,
                                                                     side_dish))


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
    """<user> - give a tasty sandwich to <user>"""
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
    """<user> - give a taco to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give a taco to that user."

    generator = textgen.TextGenerator(taco_data["templates"], taco_data["parts"],
                                      variables={"user": user})

    # act out the message
    action(generator.generate_string())
