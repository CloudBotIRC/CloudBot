"""
cryptocurrency.py

A plugin that uses the CoinMarketCap JSON API to get values for cryptocurrencies.

Created By:
    - Luke Rogers <https://github.com/lukeroge>

Special Thanks:
    - https://coinmarketcap-nexuist.rhcloud.com/

License:
    GPL v3
"""
from urllib.parse import quote_plus
from datetime import datetime

import requests

from cloudbot import hook

API_URL = "https://coinmarketcap-nexuist.rhcloud.com/api/{}"


# aliases
@hook.command("bitcoin", "btc", autohelp=False)
def bitcoin():
    """ -- Returns current bitcoin value """
    # alias
    return crypto_command("btc")


@hook.command("litecoin", "ltc", autohelp=False)
def litecoin():
    """ -- Returns current litecoin value """
    # alias
    return crypto_command("ltc")


@hook.command("dogecoin", "doge", autohelp=False)
def dogecoin():
    """ -- Returns current dogecoin value """
    # alias
    return crypto_command("doge")


@hook.command("dash", "darkcoin", autohelp=False)
def dash():
    """ -- Returns current darkcoin/dash value """
    # alias
    return crypto_command("dash")
    
    
@hook.command("zetacoin", "zet", autohelp=False)
def zet():
    """ -- Returns current Zetacoin value """
    # alias
    return crypto_command("zet")
    

# main command
@hook.command("crypto", "cryptocurrency")
def crypto_command(text):
    """ <ticker> -- Returns current value of a cryptocurrency """
    try:
        encoded = quote_plus(text)
        request = requests.get(API_URL.format(encoded))
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get value: {}".format(e)

    data = request.json()

    if "error" in data:
        return "{}.".format(data['error'])

    updated_time = datetime.fromtimestamp(data['timestamp'])
    if (datetime.today() - updated_time).days > 2:
        # the API retains data for old ticker names that are no longer updated
        # in these cases we just return a "not found" message
        return "Currency not found."

    change = float(data['change'])
    if change > 0:
        change_str = "\x033{}%\x0f".format(change)
    elif change < 0:
        change_str = "\x035{}%\x0f".format(change)
    else:
        change_str = "{}%".format(change)

    return "{} // \x0307${:,.2f}\x0f USD - {:,.7f} BTC // {} change".format(data['symbol'].upper(),
                                                                            float(data['price']['usd']),
                                                                            float(data['price']['btc']),
                                                                            change_str)
