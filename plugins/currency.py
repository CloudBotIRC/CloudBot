"""
currency.py
A plugin that uses Fixer.io API to get exchange rates for currencies.
Created By:
    - Dumle29 <https://github.com/Dumle29>
    - Fixed by Foxlet <https://furcode.co>
Special Thanks:
    - https://developer.yahoo.com/yql/guide/running-chapt.html
    - Luke Rogers <https://github.com/lukeroge> For the cryptocurrency plugin that this is based on
License:
    GPL v3
"""


from cloudbot import hook
#from cloudbot.util import database

# table = Table(
#     "exchanges",
#     database.metadata,
#     Column("currency", String(4)),
#     Column("rate", Integer, default=0),
#     Column("base", String(4)),
#     PrimaryKeyConstraint("currency")
# )

import re
import requests
from decimal import *

currency_re = re.compile(r"^([\d\.,]{1,})\s([a-zA-Z]{3})\s(in|to)\s((([a-zA-Z]{3})|([a-zA-Z]{3})\s)){1,}$")
API_URL = "http://data.fixer.io/api/latest?"

@hook.on_start()
def load_api(bot):
    global api_key

    api_key = bot.config.get("api_keys", {}).get("fixer_io", None)

@hook.regex(currency_re)
def currency_exchange(match):
    """ <value> <type> <target currency(ies)> -- converts from one type to another. Fx 10 usd in dkk eur cad"""
    text = match.group().upper().split()

    if text[2] == "IN" or text[2] == "TO" :
        text.pop(2)

    try:
        value = float(text[0])
    except ValueError:
        return "You did not input a value."

    text.pop(0)

    try:
        request = requests.get(API_URL + "access_key=" + api_key)
        request.raise_for_status()
        data = request.json()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get value: {}".format(e)

    if not data['success'] :
        return "No results returned."
    else:
        for currency in text:
            if not currency in data['rates']:
                return "{} is not a supported currency".format(currency)

        getcontext().prec = 3

        normalized = Decimal(value) / Decimal(data['rates'][text[0]])
        base_currency = text[0]
        text.pop(0)

        converted = ['%.2f' % (Decimal(normalized) * Decimal(data['rates'][currency])) + " " + currency for currency in text]

    return '{} {} is {}'.format(value, base_currency, " or ".join(converted))
