import requests
import re
from bs4 import BeautifulSoup

from cloudbot import hook
from cloudbot.util import web, formatting, colors


SEARCH_URL = "http://www.amazon.{}/s/"
REGION = "com"

AMAZON_RE = re.compile(""".*ama?zo?n\.(com|co\.uk|co\.jp|de|fr)/.*/(?:exec/obidos/ASIN/|o/|gp/product/|(?:(?:[^"\'/]*)/)?dp/|)(B[A-Z0-9]{9})""", re.I)

# Feel free to set this to None or change it to your own ID.
# Or leave it in to support CloudBot, it's up to you!
AFFILIATE_TAG = "cloudbot-20"


@hook.regex(AMAZON_RE)
def amazon_url(match):
    cc = match.group(1)
    asin = match.group(2)
    return amazon(asin, parsed=cc)


@hook.command("amazon", "az")
def amazon(text, parsed=None):
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
    if parsed:
        # input is from a link parser, we need a specific URL
        request = requests.get(SEARCH_URL.format(parsed), params=params, headers=headers)
    else:
        request = requests.get(SEARCH_URL.format(REGION), params=params, headers=headers)

    soup = BeautifulSoup(request.text)

    results = soup.find('div', {'id': 'atfResults'})
    if not results:
        if not parsed:
            return "No results found."
        else:
            return

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

    if "FREE Shipping" in item.text:
        tags.append("$(b)Free Shipping$(b)")

    try:
        price = item.find('span', {'class': 's-price'}).text
    except AttributeError:
        price = item.find('span', {'class': 'a-color-price'}).text

    try:
        pattern = re.compile(r'(product-reviews|#customerReviews)')
        rating = item.find('i', {'class': 'a-icon-star'}).find('span', {'class': 'a-icon-alt'}).text
        num_ratings = item.find('a', {'href': pattern}).text
        rating_str = "{} ({} ratings)".format(rating, num_ratings)
    except AttributeError:
        rating_str = "No Ratings"

    # generate a short url
    if AFFILIATE_TAG:
        url = "http://www.amazon.com/dp/" + asin + "/?tag=" + AFFILIATE_TAG
    else:
        url = "http://www.amazon.com/dp/" + asin + "/"

    url = web.try_shorten(url)

    tag_str = " - " + ", ".join(tags) if tags else ""

    if not parsed:
        return colors.parse("$(b){}$(b) ({}) - {}{} - {}".format(title, price, rating_str, tag_str, url))
    else:
        return colors.parse("$(b){}$(b) ({}) - {}{}".format(title, price, rating_str, tag_str))
