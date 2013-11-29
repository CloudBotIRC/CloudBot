from util import hook, http, text, web
import json


ITEM_URL = "http://www.newegg.com/Product/Product.aspx?Item={}"

@hook.command
def newegg(inp):
    """ newegg <item name> -- Searches newegg.com for <item name> """

    request = {
    "PageNumber": 1,
    "BrandId": -1,
    "NValue": "",
    "StoreDepaId": -1,
    "NodeId": -1,
    "Keyword": inp,
    "IsSubCategorySearch": False,
    "SubCategoryId": -1,
    "Sort": "FEATURED",
    "CategoryId": -1,
    "IsUPCCodeSearch": False
    }

    r = http.get_json(
      'http://www.ows.newegg.com/Search.egg/Advanced', 
      post_data = json.dumps(request)
    )

    item = r["ProductListItems"][0]

    data = {
        'title': text.truncate_str(item["Title"], 50),
        'rating': item["ReviewSummary"]["Rating"],
        'ratingcount': item["ReviewSummary"]["TotalReviews"][1:-1]
    }
    print item

    if not item["FinalPrice"] ==  item["OriginalPrice"]:
        data['price'] = "{FinalPrice}, was {OriginalPrice}".format(**item)
    else:
        data['price'] = item["FinalPrice"]

    tags = []

    if item["Instock"]:
        tags.append("\x02Stock Available\x02")
    else:
        tags.append("\x02Out Of Stock\x02")

    if item["FreeShippingFlag"]:
        tags.append("\x02Free Shipping\x02")

    if item["IsFeaturedItem"]:
        tags.append("\x02Featured\x02")

    data["tags"] = ", ".join(tags)

    data["url"] = web.try_isgd(ITEM_URL.format(item["NeweggItemNumber"]))

    return "\x02{title}\x02 ({price}) - Rated {rating}/5 ({ratingcount} ratings) - {tags} - {url}".format(**data)