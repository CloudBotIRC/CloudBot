import requests

from cloudbot import hook


# CONSTANTS

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


# HOOK FUNCTIONS

@hook.command("btc", "bitcoin", autohelp=False)
def bitcoin(text, notice):
    """[bitpay|coinbase|bitstamp] - gets bitcoin exchange rate using <exchange>, defaulting to blockchain
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
        exchange = exchanges["bitstamp"]

    response = requests.get(exchange["api_url"])
    if response.status_code != requests.codes.ok:
        return "Error reaching {}: {}".format(text or "blockchain", response.status_code)
    func = exchange["func"]
    return func(response.json())


@hook.command("ltc", "litecoin", autohelp=False)
def litecoin(message):
    """- gets litecoin exchange rate from BTC-E"""
    response = requests.get("https://btc-e.com/api/2/ltc_usd/ticker")
    if response.status_code != requests.codes.ok:
        return "Error reaching btc-e.com: {}".format(response.status_code)
    data = response.json()
    ticker = data['ticker']
    message("Current: \x0307${:,.2f}\x0f - High: \x0307${:,.2f}\x0f"
            " - Low: \x0307${:,.2f}\x0f - Volume: {:,.2f} LTC".format(ticker['buy'], ticker['high'], ticker['low'],
                                                                      ticker['vol_cur']))
