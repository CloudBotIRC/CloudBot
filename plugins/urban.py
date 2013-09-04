from util import hook, http, text
import re

base_url = 'http://www.urbandictionary.com/iphone/search/define'


@hook.command('u')
@hook.command
def urban(inp):
    """urban <phrase> [id] -- Looks up <phrase> on urbandictionary.com."""

    # clean and split the input
    input = inp.lower().strip()
    parts = input.split()

    # if the last word is a number, set the ID to that number
    if parts[-1].isdigit():
        id = int(parts[-1])
        # remove the ID from the input string
        del parts[-1]
        input = " ".join(parts)
    else:
        id = 1

    # fetch the definitions
    page = http.get_json(base_url, term=input, referer="http://m.urbandictionary.com")
    defs = page['list']
    print page

    if page['result_type'] == 'no_results':
        return 'Not found.'

    # try getting the requested definition
    try:
        definition = defs[id - 1]['definition'].replace('\r\n', ' ')
        definition = re.sub('\s+', ' ', definition).strip()  # remove excess spaces
        definition = text.truncate_str(definition, 200)
    except IndexError:
        return 'Not found.'

    url = defs[id - 1]['permalink']

    output = u"[%i/%i] %s :: %s" % \
             (id, len(defs), definition, url)

    return output
