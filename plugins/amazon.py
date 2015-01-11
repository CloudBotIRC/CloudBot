import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from cloudbot import hook
from cloudbot.util import web, formatting


SEARCH_URL = "http://www.amazon.com/s/"


@hook.command("amazon", "az")
def amazon(text):
    """ <query> -- Searches Amazon for query"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.4 (KHTML, '
                      'like Gecko) Chrome/22.0.1229.79 Safari/537.4',
        'Referer': 'http://www.amazon.com/'
    }
    params = {
        'url': 'search-alias',
        'field-keywords': text.strip()
    }
    request = requests.get(SEARCH_URL, params=params, headers=headers)
    soup = BeautifulSoup(request.text)

    results = soup.find('div', {'id': 'atfResults'})
    if not results:
        return "No results found."

    results = results.find('ul', {'id': 's-results-list-atf'}).find_all('li', {'class': 's-result-item'})
    item = results[0]
    asin = item['data-asin']

    # here we use dirty html scraping to get everything we need
    title = formatting.truncate_str(item.find('h2', {'class': 's-access-title'}).text, 50)
    tags = []

    # tags!
    if item.find('i', {'class': 'a-icon-prime'}):
        tags.append("\x02Prime\x02")

    if item.find('i', {'class': 'sx-bestseller-badge-primary'}):
        tags.append("\x02Bestseller\x02")

    if "FREE Shipping" in item.text:
        tags.append("\x02Free Shipping\x02")

    try:
        price = item.find('span', {'class': 's-price'}).text
    except AttributeError:
        price = item.find('span', {'class': 'a-color-price'}).text

    try:
        pattern = re.compile(r'product-reviews')
        rating = item.find('i', {'class': 'a-icon-star'}).find('span', {'class': 'a-icon-alt'}).text
        num_ratings = item.find('a', {'href': pattern}).text
        rating_str = "{} ({} ratings)".format(rating, num_ratings)
    except AttributeError:
        rating_str = "No Ratings"

    # clean up garbage url
    url = "http://www.amazon.com/dp/" + asin + "/?tag=cloudbot-20"
    url = web.try_shorten(url)

    tag_str = " - " + ", ".join(tags) if tags else ""

    return "\x02{}\x02 ({}) - {}{} - {}".format(title, price, rating_str, tag_str, url)
