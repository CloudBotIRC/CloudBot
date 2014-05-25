"""
cookie.py: A plugin to serve cookies to users

(c) 2014 Techman <michael@techmansworld.com>

Plugin produced under guidance of the cake plugin. Thanks!
"""
# coding=utf-8
import re
import random

from util import hook

cookies = ['Chocolate Chip', 'Oatmeal', 'Sugar', 'Oatmeal Rasin', 'Macadamia Nut', 'Jam Thumbprint', 'Medican Wedding', 'Biscotti', 'Oatmeal Cranberry', 'Chocolate Fudge', 'Peanut Butter', 'Pumpkin', 'Lemon Bar', 'Chocolate Oatmeal Fudge', 'Toffee Peanut', 'Danish Sugar', 'Tripple Chocolate', 'Oreo']

@hook.command
def cookie(inp, action=None):
    """cookie <user> - Gives <user> a cookie"""
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        return "I can't give a cookie to that user!"

    cookie_type = random.choice(cookies)
    size = random.choice(['small', 'little', 'medium-sized', 'large', 'gigantic'])
    flavor = random.choice(['tasty', 'delectable', 'delicious', 'yummy', 'toothsome', 'scrumptious', 'luscious'])
    method = random.choice(['makes', 'gives', 'gets', 'buys'])
    side_dish = random.choice(['glass of milk', 'bowl of ice cream', 'bowl of chocolate sauce'])

    action("{} {} a {} {} {} cookie and serves it with a {}!".format(method, inp, flavor, size, cookie_type, side_dish))
