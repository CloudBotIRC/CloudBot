import re
import random

from util import hook, http, text


base_url = 'http://api.urbandictionary.com/v0'
define_url = base_url + "/define"
random_url = base_url + "/random"

@hook.command('u', autohelp=False)
@hook.command(autohelp=False)
def urban(inp):
    """urban <phrase> [id] -- Looks up <phrase> on urbandictionary.com."""

    if inp:
        # clean and split the input
        inp = inp.lower().strip()
        parts = inp.split()

        # if the last word is a number, set the ID to that number
        if parts[-1].isdigit():
            id_num = int(parts[-1])
            # remove the ID from the input string
            del parts[-1]
            inp = " ".join(parts)
        else:
            id_num = 1

        # fetch the definitions
        page = http.get_json(define_url, term=inp, referer="http://m.urbandictionary.com")

        if page['result_type'] == 'no_results':
            return 'Not found.'
    else:
        # get a random definition!
        page = http.get_json(random_url, referer="http://m.urbandictionary.com")
        id_num = None

    definitions = page['list']

    if id_num:
        # try getting the requested definition
        try:
            definition = definitions[id_num - 1]

            def_text = " ".join(definition['definition'].split())  # remove excess spaces
            def_text = text.truncate_str(def_text, 200)
        except IndexError:
            return 'Not found.'

        url = definition['permalink']
        output = u"[%i/%i] %s :: %s" % \
                 (id_num, len(definitions), def_text, url)

    else:
        definition = random.choice(definitions)

        def_text = " ".join(definition['definition'].split())  # remove excess spaces
        def_text = text.truncate_str(def_text, 200)

        name = definition['word']
        url = definition['permalink']
        output = u"\x02{}\x02: {} :: {}".format(name, def_text, url)

    return output
