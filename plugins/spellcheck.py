import enchant
from util import hook

locale = "en_US"


@hook.command
def spell(inp):
    """spell <word> -- Check spelling of <word>."""

    if ' ' in inp:
        return "This command only supports one word at a time."

    if not enchant.dict_exists(locale):
        return "Could not find dictionary: {}".format(locale)

    dictionary = enchant.Dict(locale)
    is_correct = dictionary.check(inp)
    suggestions = dictionary.suggest(inp)
    s_string = ', '.join(suggestions[:10])

    if is_correct:
        return '"{}" appears to be \x02valid\x02! ' \
               '(suggestions: {})'.format(inp, s_string)
    else:
        return '"{}" appears to be \x02invalid\x02! ' \
               '(suggestions: {})'.format(inp, s_string)
