import re
import enchant
from util import hook

locale = "en_US"


@hook.command("spellcheck")
def spell(inp):
    "spell <word> -- Check spelling of <word>."

    if ' ' in inp:
        return "This command only supports one word at a time."

    if not enchant.dict_exists(locale):
        return "Could not find dictionary: %s" % locale

    dict = enchant.Dict(locale)
    is_correct = dict.check(inp)
    suggestions = dict.suggest(inp)
    s_string = ', '.join(suggestions[:10])

    if is_correct:
        return '"%s" appears to be \x02valid\x02! ' \
               '(suggestions: %s)' % (inp, s_string)
    else:
        return '"%s" appears to be \x02invalid\x02! ' \
               '(suggestions: %s)' % (inp, s_string)
