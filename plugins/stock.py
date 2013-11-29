import random

from util import hook, http, web


@hook.command
def stock(inp):
    """stock <symbol> -- gets stock information"""
    sym = inp.strip().lower()

    query = "SELECT * FROM yahoo.finance.quote WHERE symbol=@symbol LIMIT 1"
    quote = web.query(query, {"symbol": sym}).one()

    # if we dont get a company name back, the symbol doesn't match a company
    if quote['Change'] is None:
        return "unknown ticker symbol %s" % inp

    change = float(quote['Change'])
    price = float(quote['LastTradePriceOnly'])

    if change < 0:
        quote['color'] = "5"
    else:
        quote['color'] = "3"

    quote['PercentChange'] = 100 * change / (price - change)

    ret = "\x02%(Name)s\x02 (\x02%(symbol)s\x02) - %(LastTradePriceOnly)s "                   \
          "\x03%(color)s%(Change)s (%(PercentChange).2f%%)\x03 "        \
          "Day Range: %(DaysRange)s " \
          "MCAP: %(MarketCapitalization)s" % quote

    return ret
