import urllib.parse

from util import hook, http, urlnorm


@hook.command
def down(inp):
    """down <url> -- Checks if the site at <url> is up or down.
    :type inp: str
    """

    if not inp.startswith("http://"):
        inp = 'http://' + inp

    inp = 'http://' + urllib.parse.urlparse(inp).netloc

    try:
        http.get(inp, get_method='HEAD')
        return '{} seems to be up'.format(inp)
    except http.URLError:
        return '{} seems to be down'.format(inp)


@hook.command
def isup(inp):
    """isup -- uses isup.me to see if a site is up or not
    :type inp: str
    """

    # slightly overcomplicated, esoteric URL parsing
    scheme, auth, path, query, fragment = urllib.parse.urlsplit(inp.strip())

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
