from util import hook, web


@hook.command
def stock(inp):
    """stock <symbol> -- gets stock information"""
    sym = inp.strip().lower()

    query = "SELECT * FROM yahoo.finance.quote WHERE symbol=@symbol LIMIT 1"
    quote = web.query(query, {"symbol": sym}).one()

    # if we don't get a company name back, the symbol doesn't match a company
    if quote['Change'] is None:
        return "Unknown ticker symbol: {}".format(sym)

    change = float(quote['Change'])
    price = float(quote['LastTradePriceOnly'])

    if change < 0:
        quote['color'] = "5"
    else:
        quote['color'] = "3"

    quote['PercentChange'] = 100 * change / (price - change)
    print quote

    return u"\x02{Name}\x02 (\x02{symbol}\x02) - {LastTradePriceOnly} " \
           "\x03{color}{Change} ({PercentChange:.2f}%)\x03 " \
           "Day Range: {DaysRange} " \
           "MCAP: {MarketCapitalization}".format(**quote)
