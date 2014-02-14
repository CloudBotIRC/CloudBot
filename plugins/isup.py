import urlparse

from util import hook, http, urlnorm


@hook.command
def isup(inp):
    """isup -- uses isup.me to see if a site is up or not"""

    # slightly overcomplicated, esoteric URL parsing
    scheme, auth, path, query, fragment = urlparse.urlsplit(inp.strip())

    domain = auth.encode('utf-8') or path.encode('utf-8')
    url = urlnorm.normalize(domain, assume_scheme="http")

    try:
        soup = http.get_soup('http://isup.me/' + domain)
    except http.HTTPError, http.URLError:
        return "Could not get status."

    content = soup.find('div').text.strip()

    if "not just you" in content:
        return "It's not just you. {} looks \x02\x034down\x02\x0f from here!".format(url)
    elif "is up" in content:
        return "It's just you. {} is \x02\x033up\x02\x0f.".format(url)
    else:
        return "Huh? That doesn't look like a site on the interweb."
