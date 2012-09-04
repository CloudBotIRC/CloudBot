from util import hook, http, urlnorm


@hook.command
def title(inp):
    "title <url> -- gets the title of a web page"
    url = urlnorm.normalize(inp.encode('utf-8'))

    try:
        page = http.get_html(url)
    except:
        return "Could not fetch page."

    try:
        title = page.find(".//title").text
    except:
        return "Could not find title."

    title = http.unescape(title)

    return title
