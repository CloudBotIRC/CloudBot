import re

from util import hook, http, text


base_url = 'http://www.urbandictionary.com/iphone/search/define'


@hook.command('u')
@hook.command
def urban(inp):
    """urban <phrase> [id] -- Looks up <phrase> on urbandictionary.com."""

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
    page = http.get_json(base_url, term=inp, referer="http://m.urbandictionary.com")
    definitions = page['list']

    if page['result_type'] == 'no_results':
        return 'Not found.'

    # try getting the requested definition
    try:
        definition = definitions[id_num - 1]['definition'].replace('\r\n', ' ')
        definition = re.sub('\s+', ' ', definition).strip()  # remove excess spaces
        definition = text.truncate_str(definition, 200)
    except IndexError:
        return 'Not found.'

    url = definitions[id_num - 1]['permalink']

    output = u"[%i/%i] %s :: %s" % \
             (id_num, len(definitions), definition, url)

    return output
