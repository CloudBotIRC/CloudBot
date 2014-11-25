""" plugin by _303 (?)
"""

import asyncio
import re

from cloudbot import hook

pattern = re.compile(r'^(?P<count>\d+)x (?P<name>.+?): (?P<ingredients>.*)$')

recipelist = []


class Recipe(object):
    __slots__ = 'output', 'count', 'ingredients', 'line'

    def __init__(self, output, count, ingredients, line):
        self.output = output
        self.count = count
        self.ingredients = ingredients
        self.line = line

    def __str__(self):
        return self.line


with open("./data/recipes.txt") as f:
    for _line in f.readlines():
        if _line.startswith("//"):
            continue
        _line = _line.strip()
        match = pattern.match(_line)
        if not match:
            continue
        recipelist.append(Recipe(line=_line,
                                 output=match.group("name").lower(),
                                 ingredients=match.group("ingredients"),
                                 count=match.group("count")))


@asyncio.coroutine
@hook.command("mccraft", "mcrecipe")
def mcrecipe(text, reply):
    """<item> -- gets the crafting recipe for <item>"""
    text = text.lower().strip()

    results = [recipe.line for recipe in recipelist
               if text in recipe.output]

    if not results:
        return "No matches found."

    if len(results) > 3:
        reply("There are too many options, please narrow your search. ({})".format(len(results)))
        return

    for result in results:
        reply(result)
