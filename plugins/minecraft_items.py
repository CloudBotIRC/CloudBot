""" plugin by _303 (?)
"""

import re

from util import hook


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


with open("plugins/data/recipes.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        line = line.strip()
        match = pattern.match(line)
        if not match:
            continue
        recipelist.append(Recipe(line=line,
                                 output=match.group("name").lower(),
                                 ingredients=match.group("ingredients"),
                                 count=match.group("count")))

ids = []

with open("plugins/data/itemids.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        parts = line.strip().split()
        itemid = parts[0]
        name = " ".join(parts[1:])
        ids.append((itemid, name))


@hook.command("mcid")
@hook.command
def mcitem(inp, reply=None):
    """mcitem <item/id> -- gets the id from an item or vice versa"""
    inp = inp.lower().strip()

    if inp == "":
        reply("error: no input.")
        return

    results = []

    for item_id, item_name in ids:
        if inp == item_id:
            results = ["\x02[{}]\x02 {}".format(item_id, item_name)]
            break
        elif inp in item_name.lower():
            results.append("\x02[{}]\x02 {}".format(item_id, item_name))

    if not results:
        return "No matches found."

    if len(results) > 12:
        reply("There are too many options, please narrow your search. ({})".format(str(len(results))))
        return

    out = ", ".join(results)

    return out


@hook.command("mccraft")
@hook.command
def mcrecipe(inp, reply=None):
    """mcrecipe <item> -- gets the crafting recipe for an item"""
    inp = inp.lower().strip()

    results = [recipe.line for recipe in recipelist
               if inp in recipe.output]

    if not results:
        return "No matches found."

    if len(results) > 3:
        reply("There are too many options, please narrow your search. ({})".format(len(results)))
        return

    for result in results:
        reply(result)
