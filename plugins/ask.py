"""
ask.py - Ask Module
Copyright 2011, Michael Yanovich, yanovich.net
Licensed under the Eiffel Forum License 2.

More info:
 * Jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""
from cloudbot import hook
import random
import time


@hook.command("ask", autohelp=False)
def ask(text):
    """.ask <item1> or <item2> or <item3> - Randomly picks from a set
    of items seperated by ' or '."""

    choices = text
    random.seed()

    if choices is None:
        return("There is no spoon! Please try a valid question.")
    else:
        list_choices = choices.split(" or ")
        if len(list_choices) == 1:
            return (random.choice(['yes', 'no', 'What are you a fucking '
                                   'toddler? Ask your mother!']))
        else:
            return str((random.choice(list_choices)))
