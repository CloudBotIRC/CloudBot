import re
from googlefinance import getQuotes

from cloudbot import hook
import MySQLdb

stock_re = re.compile(r'^(,)([-_a-zA-Z0-9]+)', re.I)

def getTickerName(ticker):
	cnx = MySQLdb.connect(host='mysql.lan.productionservers.net', user='utilities', password='CoteP6Nev6reJeP1keq6y7HapO8I24', database='Finance')
	cursor = cnx.cursor()
	try:
		query = ("SELECT `Security Name` FROM Tickers WHERE Symbol=%(ticker)s;");
		cursor.execute(query, {"ticker": ticker})
		SymbolName = ""
		data = cursor.fetchone()
		SymbolName = data[0]
	except:
		SymbolName = "{Not in Database}"
	cursor.close()
	cnx.close()
	return SymbolName

@hook.regex(stock_re)
def stock_match(match):
    return stock(match.group(2))

@hook.command()
def stock(text):
    """<symbol> -- gets stock information"""
    sym = text.strip().lower()

    try:
	    data = getQuotes(sym)[0]
    except:
	    return "Nothing found. Learn the tickers, fool!"

    print("Data: {}".format(data))

    if not data['StockSymbol']:
        return "No results."

    quote = data

    # if we don't get a company name back, the symbol doesn't match a company
    if quote['StockSymbol'] is None:
        return "Unknown ticker symbol: {}".format(sym)

    print("StockSymbol: {}".format(quote['StockSymbol']))
    Symbol = getTickerName(quote['StockSymbol'])
    price = float(quote['LastTradePrice'].replace(',', ''))
    change = float(quote['Change'].replace(',', ''))
    quote['SymbolName'] = Symbol

    if change < 0:
        quote['color'] = "5"
    else:
        quote['color'] = "3"

    quote['PercentChange'] = 100 * change / (price - change)

    # this is for dead companies, if this isn't here PercentChange will fail with DBZ
    if price == 0 and change == 0:
        return "\x02{StockSymbol}\x02 - {LastTradePrice}".format(**quote)

    return "\x02{StockSymbol}\x02: \x02\x037{SymbolName}\x03\x02 {LastTradePrice} " \
           "\x02Change:\x02 \x03{color}{Change} ({ChangePercent}%)\x03 ".format(**quote)

