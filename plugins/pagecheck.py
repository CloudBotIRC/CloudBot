import urllib.parse

from bs4 import BeautifulSoup
import requests
import requests.exceptions

from cloudbot import hook


@hook.command("down", "offline", "up")
def down(text):
    """<url> - checks if <url> is online or offline
    :type text: str
    """

    if "://" not in text:
        text = 'http://' + text

    text = 'http://' + urllib.parse.urlparse(text).netloc

    try:
        requests.get(text)
    except requests.exceptions.ConnectionError:
        return '{} seems to be down'.format(text)
    else:
        return '{} seems to be up'.format(text)


@hook.command()
def isup(text):
    """<url> - uses isup.me to check if <url> is online or offline
    :type text: str
    """
    url = text.strip()

    # slightly overcomplicated, esoteric URL parsing
    scheme, auth, path, query, fragment = urllib.parse.urlsplit(url)

    domain = auth or path

    try:
        response = requests.get('http://isup.me/' + domain)
    except requests.exceptions.ConnectionError:
        return "Failed to get status."
    if response.status_code != requests.codes.ok:
        return "Failed to get status."

    soup = BeautifulSoup(response.text, 'lxml')

    content = soup.find('div').text.strip()

    if "not just you" in content:
        return "It's not just you. {} looks \x02\x034down\x02\x0f from here!".format(url)
    elif "is up" in content:
        return "It's just you. {} is \x02\x033up\x02\x0f.".format(url)
    else:
        return "Huh? That doesn't look like a site on the interweb."
