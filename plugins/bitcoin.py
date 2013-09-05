from util import http, hook


@hook.command(autohelp=False)
def bitcoin(inp, say=None):
    """bitcoin -- gets current exchange rate for bitcoins from mtgox"""
    data = http.get_json("https://data.mtgox.com/api/2/BTCUSD/money/ticker")
    data = data['data']
    ticker = {
        'buy': data['buy']['display_short'],
        'high': data['high']['display_short'],
        'low': data['low']['display_short'],
        'vol': data['vol']['display_short'],
    }
    say("Current: \x0307{}\x0f - High: \x0307{}\x0f"
        " - Low: \x0307{}\x0f - Volume: {}".format(data['buy'],data['high'],data['low'],data['vol']))
