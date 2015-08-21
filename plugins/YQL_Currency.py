"""
YQL_Currency.py

A plugin that uses Yahoos YQL API to get exchange rates for currencies.

Created By:
    - Dumle29 <https://github.com/Dumle29>

Special Thanks:
    - https://developer.yahoo.com/yql/guide/running-chapt.html
    - Luke Rogers <https://github.com/lukeroge> For the cryptocurrency plugin that this is based on

License:
    GPL v3
"""
from urllib.parse import urlencode

import requests

from cloudbot import hook

API_URL = "http://query.yahooapis.com/v1/public/yql?{}"

wrong_syntax_message = 'Syntax for the currency plugin is: <initial value> <initial currency> in <new currency> [additional currency(ies)], for example: 50 DKK in USD EUR GBP'

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# main command
@hook.command("moneh", "exchange")
def yahoo_finance_xchange(text):
    """ <ticker> -- Returns currency conversion from a specified currency to multiple target currencies"""
    text_list = text.upper().split()

    if not is_number(text_list[0]): # A small test to see that the user has at least provided a value to be converted
        return wrong_syntax_message

    initial_currency = text_list[1] # Assume element 1 of the list provided is a currency (and the one to convert from)
    currency_query = "" # Make an empty string to build our query in

    for (i, item) in enumerate(text_list):
        if i==3: # When we are past the initial 3 elements (40 USD in) we save the first currency to convert to
            currency_query += '"' + initial_currency + item + '"' # Yahoo takes the conversion queries as: "USDDKK" to mean USD to DKK
        elif i>3:
            currency_query += ',"' + initial_currency + item + '"' # If there's more than one currency to convert to, add them to the query list, with a comma seperator

    query = 'select * from yahoo.finance.xchange where pair in ({})'.format(currency_query) # The query to pass yahoo

    try:
        encoded = urlencode({'q' : query, 'env' : 'store://datatables.org/alltableswithkeys', 'format' : 'json'}) #URL encode the query, as well as other needed variables
        request = requests.get(API_URL.format(encoded)) # Perform the query, and save the json response
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get value: {}".format(e)

    data = request.json() # Get the data in a json format
    rates = [] # make a list to hold just the rates, and their name

    if int(data['query']['count']) < 1: # If an empty request somehow gets sent
        return "No results returned"

    if int(data['query']['count']) > 1: # If the user requests multiple conversions, the results are provided as a list
        for item in data['query']['results']['rate']:
            if item['Name'] != 'N/A':
                rates.append([item['Name'].split('/').pop(), float(item['Rate'])]) # Since the Name is written as USD/DKK, and since we are only interested in the target currency, we split by / and pop off the last element

    else: # If only one target currency is supplied, we don't get a list, just the result
        if data['query']['results']['rate']['Rate'] != 'N/A':
            rates.append([data['query']['results']['rate']['Name'].split('/').pop(), float(data['query']['results']['rate']['Rate'])])

    if len(rates) < 1: # If all rates returned above are N/A, return with this error message
        return "Please provide valid currencies"

    converted = [] # Empty list to hold converted values

    for item in rates:
        converted.append([float(text_list[0]) * float(item[1]), item[0]]) # Save a list with the values converted according to the rate, and the name of the currency

    user_string = '{} {} is '.format(text_list[0], text_list[1]) # Prepare the userstring. We already know the original currency, and the amount

    for (i, item) in enumerate(converted): # We add the converted values in a for loop, to accomodate several target currencies
        if i>0: # If the user has converted to multiple currencies, add a nice or in between
            user_string += ' or '

        user_string += '{:,.2f} {}'.format(float(item[0]), item[1]) # Add the formated converted result to the user string

    return user_string # Return the resulting string
