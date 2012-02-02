import re

from util import hook
import enchant


@hook.command("spellcheck")
def spell(inp):
    '''.time <area> -- gets the time in <area>'''
    d = enchant.Dict("en_US")

    if not (inp.split()[-1] == inp):
        return "This command only supports one word at a time."

    is_correct = d.check(inp)
    suggestions = d.suggest(inp)
    s_string = ', '.join(suggestions)

    if is_correct:
        return "That word appears to be valid! (suggestions: " + s_string + ")"
    else:
        return "That word appears to be invalid! (suggestions: " + s_string + ")"
    
