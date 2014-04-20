from util import http, hook

## CONSTANTS

exchanges = {
    "blockchain": {
        "api_url": "https://blockchain.info/ticker",
        "func": lambda data: "Blockchain // Buy: \x0307${:,.2f}\x0f -"
                             " Sell: \x0307${:,.2f}\x0f".format(data["USD"]["buy"], data["USD"]["sell"])
    },
    "coinbase": {
        "api_url": "https://coinbase.com/api/v1/prices/spot_rate",
        "func": lambda data: "Coinbase // Current: \x0307${:,.2f}\x0f".format(float(data['amount']))
    },
    "bitpay": {
        "api_url": "https://bitpay.com/api/rates",
        "func": lambda data: "Bitpay // Current: \x0307${:,.2f}\x0f".format(data[0]['rate'])
    },
    "bitstamp": {
        "api_url": "https://www.bitstamp.net/api/ticker/",
        "func": lambda data: "BitStamp // Current: \x0307${:,.2f}\x0f - High: \x0307${:,.2f}\x0f -"
                             " Low: \x0307${:,.2f}\x0f - Volume: {:,.2f} BTC".format(float(data['last']),
                                                                                     float(data['high']),
                                                                                     float(data['low']),
                                                                                     float(data['volume']))
    }
}


## HOOK FUNCTIONS

@hook.command("btc", autohelp=False)
@hook.command(autohelp=False)
def bitcoin(inp, notice=None):
    """bitcoin <exchange> -- Gets current exchange rate for bitcoins from several exchanges, default is Blockchain.
    Supports MtGox, Bitpay, Coinbase and BitStamp.
    :type inp: str
    """
    inp = inp.lower()

    if inp:
        if inp in exchanges:
            exchange = exchanges[inp]
        else:
            valid_exchanges = list(exchanges.keys())
            notice("Invalid exchange '{}', valid exchanges are {} and {}".format(inp, ", ".join(valid_exchanges[:-1]),
                                                                                 valid_exchanges[-1]))
            return
    else:
        exchange = exchanges["blockchain"]

    data = http.get_json(exchange["api_url"])
    func = exchange["func"]
    return func(data)


@hook.command("ltc", autohelp=False)
@hook.command(autohelp=False)
def litecoin(inp, message=None):
    """litecoin -- gets current exchange rate for litecoins from BTC-E
    :type inp: str
    """
    data = http.get_json("https://btc-e.com/api/2/ltc_usd/ticker")
    ticker = data['ticker']
    message("Current: \x0307${:,.2f}\x0f - High: \x0307${:,.2f}\x0f"
            " - Low: \x0307${:,.2f}\x0f - Volume: {:,.2f} LTC".format(ticker['buy'], ticker['high'], ticker['low'],
                                                                      ticker['vol_cur']))
