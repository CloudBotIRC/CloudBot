# coding=utf-8
import re
import random

from util import hook

cakes = ['Chocolate', 'Ice Cream', 'Angel', 'Boston Cream', 'Birthday', 'Bundt', 'Carrot', 'Coffee', 'Devils', 'Fruit', 'Gingerbread', 'Pound', 'Red Velvet', 'Stack', 'Welsh', 'Yokan']


@hook.command
def cake(inp, action=None):
    """cake <user> - Gives <user> an awesome cake."""
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        return "I can't give an awesome cake to that user!"

    cake_type = random.choice(cakes)
    size = random.choice(['small', 'little', 'mid-sized', 'medium-sized', 'large', 'gigantic'])
    flavor = random.choice(['tasty', 'delectable', 'delicious', 'yummy', 'toothsome', 'scrumptious', 'luscious'])
    method = random.choice(['makes', 'gives', 'gets', 'buys'])
    side_dish = random.choice(['glass of chocolate milk', 'bowl of ice cream', 'jar of cookies', 'bowl of chocolate sauce'])

    action("{} {} a {} {} {} cake and serves it with a small {}!".format(method, inp, flavor, size, cake_type, side_dish))
