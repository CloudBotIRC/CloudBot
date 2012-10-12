from util import hook, http, urlnorm


@hook.command
def title(inp):
    "title <url> -- gets the title of a web page"
    url = urlnorm.normalize(inp.encode('utf-8'), assume_scheme="http")

    try:
        page = http.get_html(url)
    except (http.HTTPError, http.URLError):
        return "Could not fetch page."

    try:
        title = page.find(".//title").text
    except AttributeError:
        return "Could not find title."

    return http.unescape(title)
