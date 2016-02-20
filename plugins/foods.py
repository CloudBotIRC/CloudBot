import codecs
import json
import os
import random
import asyncio
import re

from cloudbot import hook
from cloudbot.util import textgen

nick_re = re.compile("^[A-Za-z0-9_|.\-\]\[\{\}]*$", re.I)

cakes = ['Chocolate', 'Ice Cream', 'Angel', 'Boston Cream', 'Birthday', 'Bundt', 'Carrot', 'Coffee', 'Devils', 'Fruit',
         'Gingerbread', 'Pound', 'Red Velvet', 'Stack', 'Welsh', 'Yokan']

cookies = ['Chocolate Chip', 'Oatmeal', 'Sugar', 'Oatmeal Raisin', 'Macadamia Nut', 'Jam Thumbprint', 'Medican Wedding',
           'Biscotti', 'Oatmeal Cranberry', 'Chocolate Fudge', 'Peanut Butter', 'Pumpkin', 'Lemon Bar',
           'Chocolate Oatmeal Fudge', 'Toffee Peanut', 'Danish Sugar', 'Triple Chocolate', 'Oreo']

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
    global sandwich_data, taco_data, coffee_data, noodles_data, muffin_data, \
        tea_data, keto_data, beer_data, cheese_data, pancake_data, chicken_data, \
        icecream_data, brekkie_data, doobie_data, pizza_data, chocolate_data, pasta_data

    with codecs.open(os.path.join(bot.data_dir, "sandwich.json"), encoding="utf-8") as f:
        sandwich_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "taco.json"), encoding="utf-8") as f:
        taco_data = json.load(f)
   
    with codecs.open(os.path.join(bot.data_dir, "coffee.json"), encoding="utf-8") as f:
        coffee_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "noodles.json"), encoding="utf-8") as f:
        noodles_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "muffin.json"), encoding="utf-8") as f:
        muffin_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "tea.json"), encoding="utf-8") as f:
        tea_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "keto.json"), encoding="utf-8") as f:
        keto_data = json.load(f)
    
    with codecs.open(os.path.join(bot.data_dir, "beer.json"), encoding="utf-8") as f:
        beer_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "cheese.json"), encoding="utf-8") as f:
        cheese_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "pancake.json"), encoding="utf-8") as f:
        pancake_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "chicken.json"), encoding="utf-8") as f:
        chicken_data = json.load(f)
		
    with codecs.open(os.path.join(bot.data_dir, "brekkie.json"), encoding="utf-8") as f:
        brekkie_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "icecream.json"), encoding="utf-8") as f:
        icecream_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "doobie.json"), encoding="utf-8") as f:
        doobie_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "pizza.json"), encoding="utf-8") as f:
        pizza_data = json.load(f)
    
    with codecs.open(os.path.join(bot.data_dir, "chocolate.json"), encoding="utf-8") as f:
        chocolate_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "pasta.json"), encoding="utf-8") as f:
        pasta_data = json.load(f)
		
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
                               'side of chocolate sauce'])

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

@asyncio.coroutine
@hook.command
def coffee(text, action):
    """<user> - give coffee to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give coffee to that user."

    generator = textgen.TextGenerator(coffee_data["templates"], coffee_data["parts"],
                                      variables={"user": user})
    # act out the message
    action(generator.generate_string())
    
asyncio.coroutine
@hook.command
def noodles(text, action):
    """<user> - give noodles to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give noodles to that user."

    generator = textgen.TextGenerator(noodles_data["templates"], noodles_data["parts"],
                                      variables={"user": user})
    # act out the message
    action(generator.generate_string())
    
asyncio.coroutine
@hook.command
def muffin(text, action):
    """<user> - give muffin to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give muffin to that user."

    generator = textgen.TextGenerator(muffin_data["templates"], muffin_data["parts"],
                                      variables={"user": user})
    # act out the message
    action(generator.generate_string())
    
@asyncio.coroutine
@hook.command
def tea(text, action):
    """<user> - give tea to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give tea to that user."

    generator = textgen.TextGenerator(tea_data["templates"], tea_data["parts"],
                                      variables={"user": user})
    # act out the message
    action(generator.generate_string())

@asyncio.coroutine
@hook.command
def keto(text, action):
    """<user> - give keto food to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give food to that user."

    generator = textgen.TextGenerator(keto_data["templates"], keto_data["parts"],
                                      variables={"user": user})
    # act out the message
    action(generator.generate_string())

@asyncio.coroutine
@hook.command
def beer(text, action):
    """<user> - give beer to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give beer to that user."

    generator = textgen.TextGenerator(beer_data["templates"], beer_data["parts"],
                                      variables={"user": user})
    # act out the message
    action(generator.generate_string())

@asyncio.coroutine
@hook.command
def cheese(text, action):
    """<user> - give cheese to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give cheese to that user."

    generator = textgen.TextGenerator(cheese_data["templates"], cheese_data["parts"],
                                      variables={"user": user})
    # act out the message
    action(generator.generate_string())

@asyncio.coroutine
@hook.command
def pancake(text, action):
    """<user> - give pancakes to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give pancakes to that user."

    generator = textgen.TextGenerator(pancake_data["templates"], pancake_data["parts"],
                                      variables={"user": user})

    # act out the message
    action(generator.generate_string())

@asyncio.coroutine
@hook.command
def chicken(text, action):
    """<user> - give chicken to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give chicken to that user."

    generator = textgen.TextGenerator(chicken_data["templates"], chicken_data["parts"], variables={"user": user})

    # act out the message
    action(generator.generate_string())

@asyncio.coroutine
@hook.command
def icecream(text, action):
    """<user> - give icecream to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give icecream to that user."

    generator = textgen.TextGenerator(icecream_data["templates"], icecream_data["parts"], variables={"user": user})

    # act out the message
    action(generator.generate_string())
	
@asyncio.coroutine
@hook.command("brekky", "brekkie")
def brekkie(text, action):
    """<user> - give brekkie to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give brekkie to that user."

    generator = textgen.TextGenerator(brekkie_data["templates"], brekkie_data["parts"], variables={"user": user})

    # act out the message
    action(generator.generate_string())

@asyncio.coroutine
@hook.command("doobie")
def doobie(text, action):
    """<user> - pass the doobie to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't pass the doobie to that user."

    generator = textgen.TextGenerator(doobie_data["templates"], doobie_data["parts"], variables={"user": user})

    # act out the message
    action(generator.generate_string())

@asyncio.coroutine
@hook.command("pizza")
def pizza(text, action):
    """<user> - give pizza to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give pizza to that user."

    generator = textgen.TextGenerator(pizza_data["templates"], pizza_data["parts"], variables={"user": user})

    # act out the message
    action(generator.generate_string())
   
@asyncio.coroutine
@hook.command("chocolate")
def chocolate(text, action):
    """<user> - give chocolate to <user>"""
    user = text.strip()
    
    if not is_valid(user):
        return "I can't give chocolate to that user."
        
    generator = textgen.TextGenerator(chocolate_data["templates"], chocolate_data["parts"], variables={"user": user})
    # act out the message
    action(generator.generate_string())

@asyncio.coroutine
@hook.command
def pasta(text, action):
    """<user> - give pasta to <user>"""
    user = text.strip()

    if not is_valid(user):
        return "I can't give pasta to that user."

    generator = textgen.TextGenerator(pasta_data["templates"], pasta_data["parts"], variables={"user": user})

    # act out the message
    action(generator.generate_string())