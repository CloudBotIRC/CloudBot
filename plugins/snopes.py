import re

import requests
from lxml import html

from cloudbot import hook
from cloudbot.util import formatting, web


search_url = "http://search.atomz.com/search/?sp_a=00062d45-sp00000000"


@hook.command
def snopes(text):
    """snopes <topic> -- Searches snopes for an urban legend about <topic>."""

    try:
        params = {'sp_q': text, 'sp_c': "1"}
        request = requests.get(search_url, params=params)
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Error finding results: {}".format(e)

    search_page = html.fromstring(request.text)
    result_urls = search_page.xpath("//a[@target='_self']/@href")

    if not result_urls:
        return "No matching pages found."

    try:
        _request = requests.get(result_urls[0])
        _request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Error finding results: {}".format(e)

    snopes_page = html.fromstring(_request.text)
    snopes_text = snopes_page.text_content()

    claim = re.search(r"Claim: .*", snopes_text).group(0).strip()
    status = re.search(r"Status: .*", snopes_text)

    if status is not None:
        status = status.group(0).strip()
    else:  # new-style statuses
        status = "Status: {}".format(re.search(r"FALSE|TRUE|MIXTURE|UNDETERMINED",
                                               snopes_text).group(0).title())

    status = " ".join(status.split())  # compress whitespace
    claim = formatting.truncate(" ".join(claim.split()), 150)

    url = web.try_shorten(result_urls[0])

    return '"{}" {} - {}'.format(claim, status, url)
