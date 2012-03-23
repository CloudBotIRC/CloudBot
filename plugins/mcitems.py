""" plugin by _303 (?)
"""

from util import hook
import re
import itertools

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


with open("./plugins/data/recipes.txt") as f:
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

with open("./plugins/data/itemids.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        parts = line.strip().split()
        id = parts[0]
        name = " ".join(parts[1:])
        ids.append((id, name))


@hook.command
def itemid(input, reply=None):
    ".itemid <item/id> -- gets the id from an item or vice versa"
    input = input.lower().strip()

    if input == "":
        reply("error: no input.")
        return

    results = []

    for id, name in ids:
        if input == id:
            results = ["\x02[%s]\x02 %s" % (id, name)]
            break
        elif input in name.lower():
            results.append("\x02[%s]\x02 %s" % (id, name))

    if not len(results):
        reply("No matches found.")
        return

    if len(results) > 12:
        reply("There are too many options, please narrow your search."
              "(%s)" % len(results))
        return

    out = ", ".join(results)

    return out


@hook.command("craft")
@hook.command
def recipe(input, reply=None):
    ".recipe/.craft <item> -- gets the crafting recipe for an item"
    input = input.lower().strip()

    results = []

    for recipe in recipelist:
        if input in recipe.output:
            results.append(recipe.line)

    if not len(results):
        reply("No matches found.")
        return

    if len(results) > 3:
        reply("There are too many options, please narrow your search."
              "(%s)" % len(results))
        return

    for result in results:
        reply(result)
