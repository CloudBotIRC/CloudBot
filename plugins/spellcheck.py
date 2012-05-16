import re
import enchant
from util import hook

locale = "en_US"


@hook.command("spellcheck")
def spell(inp):
    "spell <word> -- Check spelling of <word>."
    word = inp
	
    if ' ' in word:
        return "This command only supports one word at a time."

    if not enchant.dict_exists(locale):
        return "Could not find dictionary: %s" % locale

    dict = enchant.Dict(locale)

    is_correct = dict.check(word)
    suggestions = dict.suggest(word)
    s_string = ', '.join(suggestions[:10])

    if is_correct:
        return '"%s" appears to be \x02valid\x02! ' \
               '(suggestions: %s)' % (word, s_string)
    else:
        return '"%s" appears to be \x02invalid\x02! ' \
               '(suggestions: %s)' % (word, s_string)