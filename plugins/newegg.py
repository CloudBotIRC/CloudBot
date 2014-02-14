import json
import re

from util import hook, http, text, web


## CONSTANTS

ITEM_URL = "http://www.newegg.com/Product/Product.aspx?Item={}"

API_PRODUCT = "http://www.ows.newegg.com/Products.egg/{}/ProductDetails"
API_SEARCH = "http://www.ows.newegg.com/Search.egg/Advanced"

NEWEGG_RE = (r"(?:(?:www.newegg.com|newegg.com)/Product/Product\.aspx\?Item=)([-_a-zA-Z0-9]+)", re.I)


## OTHER FUNCTIONS

def format_item(item, show_url=True):
    """ takes a newegg API item object and returns a description """
    title = text.truncate_str(item["Title"], 50)

    # format the rating nicely if it exists
    if not item["ReviewSummary"]["TotalReviews"] == "[]":
        rating = "Rated {}/5 ({} ratings)".format(item["ReviewSummary"]["Rating"],
                                                  item["ReviewSummary"]["TotalReviews"][1:-1])
    else:
        rating = "No Ratings"

    if not item["FinalPrice"] == item["OriginalPrice"]:
        price = "{FinalPrice}, was {OriginalPrice}".format(**item)
    else:
        price = item["FinalPrice"]

    tags = []

    if item["Instock"]:
        tags.append("\x02Stock Available\x02")
    else:
        tags.append("\x02Out Of Stock\x02")

    if item["FreeShippingFlag"]:
        tags.append("\x02Free Shipping\x02")

    if item["IsFeaturedItem"]:
        tags.append("\x02Featured\x02")

    if item["IsShellShockerItem"]:
        tags.append(u"\x02SHELL SHOCKER\u00AE\x02")

    # join all the tags together in a comma separated string ("tag1, tag2, tag3")
    tag_text = u", ".join(tags)

    if show_url:
        # create the item URL and shorten it
        url = web.try_isgd(ITEM_URL.format(item["NeweggItemNumber"]))
        return u"\x02{}\x02 ({}) - {} - {} - {}".format(title, price, rating,
                                                        tag_text, url)
    else:
        return u"\x02{}\x02 ({}) - {} - {}".format(title, price, rating,
                                                   tag_text)


## HOOK FUNCTIONS

@hook.regex(*NEWEGG_RE)
def newegg_url(match):
    item_id = match.group(1)
    item = http.get_json(API_PRODUCT.format(item_id))
    return format_item(item, show_url=False)


@hook.command
def newegg(inp):
    """newegg <item name> -- Searches newegg.com for <item name>"""

    # form the search request
    request = {
        "Keyword": inp,
        "Sort": "FEATURED"
    }

    # submit the search request
    r = http.get_json(
        'http://www.ows.newegg.com/Search.egg/Advanced',
        post_data=json.dumps(request)
    )

    # get the first result
    if r["ProductListItems"]:
        return format_item(r["ProductListItems"][0])
    else:
        return "No results found."


