import re

from util import hook, http, text


api_url = "http://minecraft.gamepedia.com/api.php?action=opensearch"
mc_url = "http://minecraft.gamepedia.com/"


@hook.command
def mcwiki(inp):
    """mcwiki <phrase> -- Gets the first paragraph of
    the Minecraft Wiki article on <phrase>."""

    try:
        j = http.get_json(api_url, search=inp)
    except (http.HTTPError, http.URLError) as e:
        return "Error fetching search results: {}".format(e)
    except ValueError as e:
        return "Error reading search results: {}".format(e)

    if not j[1]:
        return "No results found."

    # we remove items with a '/' in the name, because
    # gamepedia uses sub-pages for different languages
    # for some stupid reason
    items = [item for item in j[1] if not "/" in item]

    if items:
        article_name = items[0].replace(' ', '_').encode('utf8')
    else:
        # there are no items without /, just return a / one
        article_name = j[1][0].replace(' ', '_').encode('utf8')

    url = mc_url + http.quote(article_name, '')

    try:
        page = http.get_html(url)
    except (http.HTTPError, http.URLError) as e:
        return "Error fetching wiki page: {}".format(e)

    for p in page.xpath('//div[@class="mw-content-ltr"]/p'):
        if p.text_content():
            summary = " ".join(p.text_content().splitlines())
            summary = re.sub("\[\d+\]", "", summary)
            summary = text.truncate_str(summary, 200)
            return u"{} :: {}".format(summary, url)

    # this shouldn't happen
    return "Unknown Error."
