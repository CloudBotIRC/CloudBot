import urlparse

from util import hook, http


@hook.command
def down(inp):
    """down <url> -- Checks if the site at <url> is up or down."""

    if 'http://' not in inp:
        inp = 'http://' + inp

    inp = 'http://' + urlparse.urlparse(inp).netloc

    # http://mail.python.org/pipermail/python-list/2006-December/589854.html
    try:
        http.get(inp, get_method='HEAD')
        return '{} seems to be up'.format(inp)
    except http.URLError:
        return '{} seems to be down'.format(inp)
