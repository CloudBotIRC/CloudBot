import enchant
from util import hook

locale = "en_US"


@hook.command
def spell(inp):
    """spell <word/sentence> -- Check spelling of a word or sentence."""
    words = inp.split(" ")
    if words[0] == "":
        words = []
    if not enchant.dict_exists(locale):
        return "Could not find dictionary: {}".format(locale)

    dictionary = enchant.Dict(locale)

    if len(words) > 1:
        out = []
        for x in words:
            is_correct = dictionary.check(x)
            suggestions = dictionary.suggest(x)
            s_string = '/'.join(suggestions[:3])
            if is_correct:
                out.append(x)
            else:
                out.append('\x02' + s_string + '\x02')
        return " ".join(out)
    else:
        is_correct = dictionary.check(words[0])
        suggestions = dictionary.suggest(words[0])
        s_string = ', '.join(suggestions[:10])
        if is_correct:
            return '"{}" appears to be \x02valid\x02! ' \
                   '(suggestions: {})'.format(inp, s_string)
        else:
            return '"{}" appears to be \x02invalid\x02! ' \
                   '(suggestions: {})'.format(inp, s_string)
