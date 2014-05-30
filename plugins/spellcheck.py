from enchant.checker import SpellChecker
import enchant

from cloudbot import hook

locale = "en_US"


@hook.command()
def spell(text):
    """spell <word/sentence> -- Check spelling of a word or sentence."""

    if not enchant.dict_exists(locale):
        return "Could not find dictionary: {}".format(locale)

    if len(text.split(" ")) > 1:
        # input is a sentence
        checker = SpellChecker(locale)
        checker.set_text(text)

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
            text = text[:start] + s_string + text[finish:]
        return text
    else:
        # input is a word
        dictionary = enchant.Dict(locale)
        is_correct = dictionary.check(text)
        suggestions = dictionary.suggest(text)
        s_string = ', '.join(suggestions[:10])
        if is_correct:
            return '"{}" appears to be \x02valid\x02! ' \
                   '(suggestions: {})'.format(text, s_string)
        else:
            return '"{}" appears to be \x02invalid\x02! ' \
                   '(suggestions: {})'.format(text, s_string)
