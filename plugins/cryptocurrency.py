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

from cloudbot import hook

API_URL = "https://coinmarketcap-nexuist.rhcloud.com/api/{}"


# alises
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
    if not text:
        return "?"