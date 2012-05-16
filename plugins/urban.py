# Plugin by Lukeroge
from util import hook, http


@hook.command('u')
@hook.command
def urban(inp):
    "urban <phrase> [id] -- Looks up <phrase> on urbandictionary.com."

    # set a default definition number
    id = 1

    # clean and split the input
    input = inp.lower().strip()
    parts = input.split()

    # if the last word is a number, set the ID to that number
    if parts[-1].isdigit():
        id = int(parts[-1])
        # remove the ID from the input string
        del parts[-1]
        input = " ".join(parts)

    # fetch the definitions
    url = 'http://www.urbandictionary.com/iphone/search/define'
    page = http.get_json(url, term=input)
    defs = page['list']

    if page['result_type'] == 'no_results':
        return 'Not found.'

    # try getting the requested definition
    try:
        out = "[%i/%i] %s: %s" % \
              (id, len(defs), defs[id - 1]['word'],
              defs[id - 1]['definition'])
    except IndexError:
        return 'Not found.'

    if len(out) > 400:
        out = out[:out.rfind(' ', 0, 400)] + '...'

    return out
