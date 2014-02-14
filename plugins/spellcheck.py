from enchant.checker import SpellChecker
import enchant

from util import hook


locale = "en_US"


@hook.command
def spell(inp):
    """spell <word/sentence> -- Check spelling of a word or sentence."""

    if not enchant.dict_exists(locale):
        return "Could not find dictionary: {}".format(locale)

    if len(inp.split(" ")) > 1:
        # input is a sentence
        checker = SpellChecker(locale)
        checker.set_text(inp)

        offset = 0
        for err in checker:
            # find the location of the incorrect word
            start = err.wordpos + offset
            finish = start + len(err.word)
            # get some suggestions for it
            suggestions = err.suggest()
            s_string = '/'.join(suggestions[:3])
            s_string = "\x02{}\x02".format(s_string)
            # calculate the offset for the next word
            offset = (offset + len(s_string)) - len(err.word)
            # replace the word with the suggestions
            inp = inp[:start] + s_string + inp[finish:]
        return inp
    else:
        # input is a word
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
