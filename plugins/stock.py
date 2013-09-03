import random
import json

from util import hook, http

url = 'http://www.google.com/ig/api'

@hook.command
def stock(inp):
    "stock <symbol> -- Gets information about stock symbol <symbol>."

    parsed = http.get_xml(url, stock=inp)

    if len(parsed) != 1:
        return "error getting stock info"

    # Stuff the results in a dict for easy string formatting
    results = dict((el.tag, el.attrib['data'])
                   for el in parsed.xpath('//finance/*'))

    # if we dont get a company name back, the symbol doesn't match a company
    if not "company" in results:
        guessd = json.loads(http.get("http://d.yimg.com/autoc.finance.yahoo.com/autoc?query=%s&callback=YAHOO.Finance.SymbolSuggest.ssCallback" % inp)[39:-1])
        guess = guessd['ResultSet']['Result']
        if len(guess) > 0:
            guess = guess[0]["symbol"]
            return stock(guess)
        else:
            return "error: unable to get stock info for '%s'" % inp
        
    if results['last'] == '0.00':
        return "%(company)s - last known stock value was 0.00 %(currency)s" \
               " as of %(trade_timestamp)s" % (results)

    if results['change'][0] == '-':
        results['color'] = "5"
    else:
        results['color'] = "3"

    ret = "%(company)s - %(last)s %(currency)s "                   \
          "\x03%(color)s%(change)s (%(perc_change)s%%)\x03 "       \
          "as of %(trade_timestamp)s" % results

    if results['delay'] != '0':
        ret += " (delayed %s minutes)" % results['delay']

    return ret
