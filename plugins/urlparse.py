from util import hook, http, urlnorm
import re

titler = re.compile(r'(?si)<title>(.+?)</title>')


def gettitle(url):
    url = urlnorm.normalize(url.encode('utf-8'))
    url = url.decode('utf-8')
    # add http if its missing
    if url[:7] != "http://" and url[:8] != "https://":
        url = "http://" + url
    try:
        # get the title
        request = http.open(url)
        real_url = request.geturl()
        text = request.read()
        text = text.decode('utf8')
        match = titler.search(text)
        title = match.group(1)
    except:
        return "Could not parse URL! Are you sure its valid?"

    title = http.unescape(title)

    # if the url has been redirected, show us
    if real_url == url:
        return title
    else:
        return u"%s [%s]" % (title, real_url)


@hook.command
def title(inp):
    ".title <url> -- gets the title of a web page"
    return gettitle(inp)
