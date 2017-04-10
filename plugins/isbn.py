import re
import json, requests

from cloudbot import hook
import cloudbot

def getISBN(book):
    try:
        url = 'http://isbndb.com/api/v2/json/JGLRWEU7/book/'
        url = url + book
        #print(url)
        resp = requests.get(url=url)
        data = json.loads(resp.text)
        return data
    except:
        return("fail")

@hook.command()
def isbn(reply, text):
    """<isbn> -- gets book information"""
    sym = text.strip().lower()

    #print("String: {}".format(sym))
    tmpdata = getISBN(sym)
    if tmpdata == "fail":
	    return("Nothing found, try a different ISBN")
    if 'error' in tmpdata:
	    return("{}".format(tmpdata['error']))
    data = tmpdata['data'][0]
    #print("Data: {}".format(data))


    reply("ISBN Lookup | Title: \x02{title}\x02 | Physical Description: \x02{physical_description_text}\x02 | Edition Info: \x02{edition_info}\x02 | Dewey Decimal: \x02{dewey_decimal}\x02".format(**data))
    reply("Summary: {summary}".format(**data))
    for author in data['author_data']:
        reply("Author: {}".format(author['name']))
    return("Long Title: {title_long}".format(**data))

