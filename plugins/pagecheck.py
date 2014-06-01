import urllib.parse

from cloudbot import hook, http, urlnorm


@hook.command(["down", "offline", "up"])
def down(text):
    """<url> - checks if <url> is online or offline
    :type text: str
    """

    if not text.startswith("http://"):
        text = 'http://' + text

    text = 'http://' + urllib.parse.urlparse(text).netloc

    try:
        http.get(text, get_method='HEAD')
        return '{} seems to be up'.format(text)
    except http.URLError:
        return '{} seems to be down'.format(text)


@hook.command()
def isup(text):
    """<url> - uses isup.me to check if <url> is online or offline
    :type text: str
    """

    # slightly overcomplicated, esoteric URL parsing
    scheme, auth, path, query, fragment = urllib.parse.urlsplit(text.strip())

    domain = auth or path
    url = urlnorm.normalize(domain, assume_scheme="http")

    try:
        soup = http.get_soup('http://isup.me/' + domain)
    except http.HTTPError:
        return "Failed to get status."

    content = soup.find('div').text.strip()

    if "not just you" in content:
        return "It's not just you. {} looks \x02\x034down\x02\x0f from here!".format(url)
    elif "is up" in content:
        return "It's just you. {} is \x02\x033up\x02\x0f.".format(url)
    else:
        return "Huh? That doesn't look like a site on the interweb."
