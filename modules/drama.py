import re
from urllib import parse

from util import hook, http, formatting


api_url = "http://encyclopediadramatica.se/api.php?action=opensearch"
ed_url = "http://encyclopediadramatica.se/"


@hook.command
def drama(text):
    """drama <phrase> -- Gets the first paragraph of
    the Encyclopedia Dramatica article on <phrase>."""

    data = http.get_json(api_url, search=text)

    if not data[1]:
        return "No results found."
    article_name = data[1][0].replace(' ', '_')

    url = ed_url + parse.quote(article_name, '')
    page = http.get_html(url)

    for p in page.xpath('//div[@id="bodyContent"]/p'):
        if p.text_content():
            summary = " ".join(p.text_content().splitlines())
            summary = re.sub("\[\d+\]", "", summary)
            summary = formatting.truncate_str(summary, 220)
            return "{} - {}".format(summary, url)

    return "Unknown Error."
