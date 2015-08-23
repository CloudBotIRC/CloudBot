"""
yahoocurrency.py
A plugin that uses Yahoos YQL API to get exchange rates for currencies.
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

import requests
from decimal import *

API_URL = "http://query.yahooapis.com/v1/public/yql?"

@hook.command("ye", "exchange")
def yahoo_finance_exchange(text):
    """ <value> <type> <target currency(ies)> -- converts from one type to another"""
    text = text.upper().split()


    if len(text) < 3:
        return "<value> <type> <target currency(ies)> -- converts from one type to another"
        
    if text[2].lower() == "in":
        text.pop(2)

    try:
        value = float(text[0])
    except ValueError:
        return "You did not input a value."

    currencies = '"{}"'.format('", "'.join([text[1]+item for item in text[2:]]))
    query = 'select * from yahoo.finance.xchange where pair in ({})'.format(currencies)

    try:
        request = requests.get(API_URL, params={'q': query, 'env': 'store://datatables.org/alltableswithkeys', 'format': 'json'})
        request.raise_for_status()
        data = request.json()['query']
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get value: {}".format(e)

    if int(data['count']) < 1:
        return "No results returned."
    elif int(data['count']) > 1:
        try:
            rates = [(item['Name'].split('/')[1], float(item['Rate'])) for item in data['results']['rate']]
        except ValueError:
            return "Please provide valid currencies."
    else:
        if data['results']['rate']['Rate'] != 'N/A':
            rates = [data['results']['rate']['Name'].split('/')[1], float(data['results']['rate']['Rate'])]
        else:
            return "Please provide valid currencies."

    getcontext().prec = 3

    if int(data['count']) == 1:
        converted = [str(Decimal(value) * Decimal(rates[1])) + " " + rates[0]]
    else:
        converted = [str(Decimal(value) * Decimal(item[1])) + " " + item[0] for item in rates]

    return '{} {} is {}'.format(value, text[1], " or ".join(converted))
