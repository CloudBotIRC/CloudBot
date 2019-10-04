import random

import requests

from cloudbot import hook
from cloudbot.util import formatting


base_url = 'http://api.urbandictionary.com/v0'
define_url = base_url + "/define"
random_url = base_url + "/random"

# schema is from http://api.urbandictionary.com/v0/words_of_the_day?per_page=90000000&page=1&api_key=ab71d33b15d36506acf1e379b0ed07ee
definitions_per_page = 10

@hook.command("urban", "u", autohelp=False)
def urban(text):
    """urban <phrase> [id] -- Looks up <phrase> on urbandictionary.com."""

    headers = {
        "Referer": "http://m.urbandictionary.com"
    }

    if text:
        # clean and split the input
        text = text.lower().strip()
        parts = text.split()

        # if the last word is a number, set the ID to that number
        if parts[-1].isdigit():
            id_num = int(parts[-1])

            # get definitions beyond the first page
            # first page index is 1
            page_num = 1 + ((id_num - 1) // definitions_per_page)
            id_page_num = (id_num - 1) % definitions_per_page

            # remove the ID from the input string
            text = " ".join(parts[:-1])
        else:
            id_num = 1
            page_num = 1
            id_page_num = 0

        # fetch the definitions
        try:
            params = {
                        "term": text,
                        "page": page_num
                     }
            response = requests.get(define_url, params=params, headers=headers)
            response.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            return "Could not get definition: {}".format(e)

        page = response.json()

        if not page['list']:
            return 'Not found.'
    else:
        # get a random definition!
        try:
            request = requests.get(random_url, headers=headers)
            request.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            return "Could not get definition: {}".format(e)

        page = request.json()
        id_num = None

    definitions = page['list']

    if id_num:
        # try getting the requested definition
        try:
            definition = definitions[id_page_num]

            def_text = " ".join(definition['definition'].split())  # remove excess spaces
            def_text = formatting.truncate(def_text, 200)
        except IndexError:
            return 'Not found.'

        url = definition['permalink']

        output = "\x02{}\x02 {} - {}".format(id_num, def_text, url)

    else:
        definition = random.choice(definitions)

        def_text = " ".join(definition['definition'].split())  # remove excess spaces
        def_text = formatting.truncate(def_text, 200)

        name = definition['word']
        url = definition['permalink']
        output = "\x02{}\x02: {} - {}".format(name, def_text, url)

    return output
