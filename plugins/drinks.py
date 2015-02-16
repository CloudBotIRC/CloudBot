import json
import os
import random

from cloudbot import hook

@hook.onload()
def load_drinks(bot):
    """load the drink recipes"""
    global drinks
    with open(os.path.join(bot.data_dir, "drinks.json")) as json_data:
    drinks = json.load(json_data)



