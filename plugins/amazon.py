import requests
import re
from bs4 import BeautifulSoup

from cloudbot import hook
from cloudbot.util import web, formatting, colors


SEARCH_URL = "http://www.amazon.{}/s/"
REGION = "com"

AMAZON_RE = re.compile(""".*ama?zo?n\.(com|co\.uk|com\.au|de|fr|ca|cn|es|it|in)/.*/(?:exec/obidos/ASIN/|o/|gp/product/|
(?:(?:[^"\'/]*)/)?dp/|)(B[A-Z0-9]{9})""", re.I)

# Feel free to set this to None or change it to your own ID.
# Or leave it in to support CloudBot, it's up to you!
AFFILIATE_TAG = "cloudbot-20"


@hook.regex(AMAZON_RE)
def amazon_url(match):
    cc = match.group(1)
    asin = match.group(2)
    return amazon(asin, _parsed=cc)


@hook.command("amazon", "az")
def amazon(text, _parsed=False):
    """<query> -- Searches Amazon for query"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, '
                      'like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Referer': 'http://www.amazon.com/'
    }
    params = {
        'url': 'search-alias',
        'field-keywords': text.strip()
    }
    if _parsed:
        # input is from a link parser, we need a specific URL
        request = requests.get(SEARCH_URL.format(_parsed), params=params, headers=headers)
    else:
        request = requests.get(SEARCH_URL.format(REGION), params=params, headers=headers)

    soup = BeautifulSoup(request.text)

    # check if there are any results on the amazon page
    results = soup.find('div', {'id': 'atfResults'})
    if not results:
        if not _parsed:
            return "No results found."
        else:
            return

    # get the first item from the results on the amazon page
    results = results.find('ul', {'id': 's-results-list-atf'}).find_all('li', {'class': 's-result-item'})
    item = results[0]
    asin = item['data-asin']

    # here we use dirty html scraping to get everything we need
    title = formatting.truncate(item.find('h2', {'class': 's-access-title'}).text, 60)
    tags = []

    # tags!
    if item.find('i', {'class': 'a-icon-prime'}):
        tags.append("$(b)Prime$(b)")

    if item.find('i', {'class': 'sx-bestseller-badge-primary'}):
        tags.append("$(b)Bestseller$(b)")

    # we use regex because we need to recognise text for this part
    # the other parts detect based on html tags, not text
    if re.search(r"(Kostenlose Lieferung|Livraison gratuite|FREE Shipping|Envío GRATIS"
                 r"|Spedizione gratuita)", item.text, re.I):
        tags.append("$(b)Free Shipping$(b)")

    try:
        price = item.find('span', {'class': ['s-price', 'a-color-price']}).text
    except AttributeError:
        for i in item.find_all('sup', {'class': 'sx-price-fractional'}):
            i.string.replace_with('.' + i.string)
        price = item.find('span', {'class': 'sx-price'}).text

    # use a whole lot of BS4 and regex to get the ratings
    try:
        # get the rating
        rating = item.find('i', {'class': 'a-icon-star'}).find('span', {'class': 'a-icon-alt'}).text
        rating = re.search(r"([0-9]+(?:(?:\.|,)[0-9])?).*5", rating).group(1).replace(",", ".")
        # get the rating count
        pattern = re.compile(r'(product-reviews|#customerReviews)')
        num_ratings = item.find('a', {'href': pattern}).text.replace(".", ",")
        # format the rating and count into a nice string
        rating_str = "{}/5 stars ({} ratings)".format(rating, num_ratings)
    except AttributeError:
        rating_str = "No Ratings"

    # generate a short url
    if AFFILIATE_TAG:
        url = "http://www.amazon.com/dp/" + asin + "/?tag=" + AFFILIATE_TAG
    else:
        url = "http://www.amazon.com/dp/" + asin + "/"
    url = web.try_shorten(url)

    # join all the tags into a string
    tag_str = " - " + ", ".join(tags) if tags else ""

    # finally, assemble everything into the final string, and return it!
    if not _parsed:
        return colors.parse("$(b){}$(b) ({}) - {}{} - {}".format(title, price, rating_str, tag_str, url))
    else:
        return colors.parse("$(b){}$(b) ({}) - {}{}".format(title, price, rating_str, tag_str))
