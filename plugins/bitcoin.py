from util import http, hook


@hook.command(autohelp=False)
def bitcoin(inp, message=None):
    """bitcoin -- gets current exchange rate for bitcoins from mtgox"""
    data = http.get_json("https://data.mtgox.com/api/2/BTCUSD/money/ticker")
    data = data['data']
    ticker = {
        'buy': data['buy']['display_short'].encode('ascii','ignore'),
        'high': data['high']['display_short'].encode('ascii','ignore'),
        'low': data['low']['display_short'].encode('ascii','ignore'),
        'vol': data['vol']['display_short'].encode('ascii','ignore'),
    }
    message("Current: \x0307{!s}\x0f - High: \x0307{!s}\x0f"
        " - Low: \x0307{!s}\x0f - Volume: {!s}".format(ticker['buy'],ticker['high'],ticker['low'],ticker['vol']))
