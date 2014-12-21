# Based on plugin by foxcode - <https://github.com/FurCode/RoboCop2>

import requests

from cloudbot import hook


@hook.command("octopart", "octosearch")
def octopart(text):
    """octopart <keyword> -- Search for any part on the Octopart database."""
    url = "http://octopart.com/api/v3/parts/search"
    params = {
        'apikey': 'aefcd00e',
        'q': text,
        'start': 0,
        'limit': 2
    }

    try:
        request = requests.get(url, params=params)
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not fetch part data: {}".format(e)

    response = request.json()

    if not response['results']:
        return "No results."

    # get part
    result = response['results'][0]
    part = result['item']

    # print matched part
    return "{} - {} - {}".format(part['brand']['name'], part['mpn'], part['octopart_url'])
