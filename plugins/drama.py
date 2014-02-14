import re

from util import hook, http, text


api_url = "http://encyclopediadramatica.se/api.php?action=opensearch"
ed_url = "http://encyclopediadramatica.se/"


@hook.command
def drama(inp):
    """drama <phrase> -- Gets the first paragraph of
    the Encyclopedia Dramatica article on <phrase>."""

    j = http.get_json(api_url, search=inp)

    if not j[1]:
        return "No results found."
    article_name = j[1][0].replace(' ', '_').encode('utf8')

    url = ed_url + http.quote(article_name, '')
    page = http.get_html(url)

    for p in page.xpath('//div[@id="bodyContent"]/p'):
        if p.text_content():
            summary = " ".join(p.text_content().splitlines())
            summary = re.sub("\[\d+\]", "", summary)
            summary = text.truncate_str(summary, 220)
            return "{} :: {}".format(summary, url)

    return "Unknown Error."
