from cloudbot import http, hook

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

@hook.command(["btc", "bitcoin"], autohelp=False)
def bitcoin(text, notice):
    """bitcoin <exchange> -- Gets current exchange rate for bitcoins from several exchanges, default is Blockchain.
    Supports MtGox, Bitpay, Coinbase and BitStamp.
    :type text: str
    """
    text = text.lower()

    if text:
        if text in exchanges:
            exchange = exchanges[text]
        else:
            valid_exchanges = list(exchanges.keys())
            notice("Invalid exchange '{}', valid exchanges are {} and {}".format(text, ", ".join(valid_exchanges[:-1]),
                                                                                 valid_exchanges[-1]))
            return
    else:
        exchange = exchanges["blockchain"]

    data = http.get_json(exchange["api_url"])
    func = exchange["func"]
    return func(data)


@hook.command(["ltc", "litecoin"], autohelp=False)
def litecoin(message):
    """litecoin -- gets current exchange rate for litecoins from BTC-E"""
    data = http.get_json("https://btc-e.com/api/2/ltc_usd/ticker")
    ticker = data['ticker']
    message("Current: \x0307${:,.2f}\x0f - High: \x0307${:,.2f}\x0f"
            " - Low: \x0307${:,.2f}\x0f - Volume: {:,.2f} LTC".format(ticker['buy'], ticker['high'], ticker['low'],
                                                                      ticker['vol_cur']))
