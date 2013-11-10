import random

from util import hook, http


@hook.command
def stock(inp):
    """.stock <symbol> -- gets stock information"""

    url = ('http://query.yahooapis.com/v1/public/yql?format=json&'
           'env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys')

    parsed = http.get_json(url, q='select * from yahoo.finance.quote '
                           'where symbol in ("%s")' % inp)  # heh, SQLI

    quote = parsed['query']['results']['quote']

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

    ret = "%(Name)s - %(LastTradePriceOnly)s "                   \
          "\x03%(color)s%(Change)s (%(PercentChange).2f%%)\x03 "        \
          "Day Range: %(DaysRange)s " \
          "MCAP: %(MarketCapitalization)s" % quote

    return ret