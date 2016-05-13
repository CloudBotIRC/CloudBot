import requests
import random

from bs4 import BeautifulSoup
from cloudbot import hook

search_url = "http://dogpile.com/search"

HEADERS = {'User-Agent': 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19'}

opt_out = []

@hook.command("dpis", "gis")
def dogpileimage(text, chan):
    """Uses the dogpile search engine to search for images."""
    if chan in opt_out:
        return
    image_url = search_url + "/images"
    params = { 'q': " ".join(text.split())}
    r = requests.get(image_url, params=params, headers=HEADERS)
    soup = BeautifulSoup(r.content)
    linklist = soup.find('div', id="webResults").find_all('a', {'class':'resultThumbnailLink'})
    image = requests.get(random.choice(linklist)['href'], headers=HEADERS).url
    return image

@hook.command("dp", "g", "dogpile")
def dogpile(text, chan):
    """Uses the dogpile search engine to find shit on the web."""
    if chan in opt_out:
        return
    web_url = search_url + "/web"
    params = {'q':" ".join(text.split())}
    r = requests.get(web_url, params=params, headers=HEADERS)
    soup = BeautifulSoup(r.content)
    result_url = requests.get(soup.find('div', id="webResults").find_all('a', {'class':'resultDisplayUrl'})[0]['href'], headers=HEADERS).url
    result_description = soup.find('div', id="webResults").find_all('div', {'class':'resultDescription'})[0].text
    return "\x02{}\x02 -- {}".format(result_url, result_description)
