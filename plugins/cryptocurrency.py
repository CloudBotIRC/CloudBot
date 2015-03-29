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
import requests

from cloudbot import hook

from urllib.parse import quote_plus

API_URL = "https://coinmarketcap-nexuist.rhcloud.com/api/{}"


# aliases
@hook.command("bitcoin", "btc", autohelp=False)
def bitcoin():
    """ -- Returns current bitcoin value """
    # alis
    return crypto_command("btc")


@hook.command("litecoin", "ltc", autohelp=False)
def litecoin():
    """ -- Returns current litecoin value """
    # alis
    return crypto_command("ltc")


@hook.command("dogecoin", "doge", autohelp=False)
def dogecoin():
    """ -- Returns current dogecoin value """
    # alis
    return crypto_command("doge")


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
        return "{}".format(data['error'])

    return "{} // \x0307${:,.2f}\x0f USD - {:,.5f} BTC - {}% change".format(data['symbol'].upper(),
                                                                            float(data['price']['usd']),
                                                                            float(data['price']['btc']),
                                                                            data['change'])


