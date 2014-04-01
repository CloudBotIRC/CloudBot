import random

from util import hook, http, web

# set this to true to censor this plugin!
CENSOR = True

METADATA_URL = "http://omnidator.appspot.com/microdata/json/?url={}"
RANDOM_URL = "http://www.cookstr.com/searches/surprise"

PHRASES = [
    u"EAT SOME FUCKING \x02{}\x02",
    u"I'D SAY EAT SHIT, BUT THAT WOULDN'T BE HELPFUL, HOW ABOUT SOME FUCKING \x02{}\x02",
    u"YOU WON'T NOT MAKE SOME FUCKING \x02{}\x02",
    u"HOW ABOUT SOME FUCKING \x02{}\x02",
    u"WHY DON'T YOU EAT SOME FUCKING \x02{}\x02",
    u"MAKE SOME FUCKING \x02{}\x02",
    u"FEAST YOUR EYES AND SUBSEQUENTLY MOUTH ON SOME FUCKING \x02{}\x02",
    u"INDUCE FOOD COMA WITH SOME FUCKING \x02{}\x02"
]

clean_key = lambda i: i.split("#")[1]


class ParseError(Exception):
    pass


def get_data(url):
    """ Uses the omnidator API to parse the metadata from the provided URL """
    try:
        omni = http.get_json(METADATA_URL.format(url))
    except (http.HTTPError, http.URLError) as e:
        raise ParseError(e)
    schemas = omni["@"]
    for d in schemas:
        if d["a"] == "<http://schema.org/Recipe>":
            data = {clean_key(key): value for (key, value) in d.iteritems()
                    if key.startswith("http://schema.org/Recipe")}
            return data
    raise ParseError("No recipe data found")


@hook.command(autohelp=False)
def recipe(inp):
    """recipe - Gets a random recipe from cookstr.com!"""
    try:
        page = http.open(RANDOM_URL)
    except (http.HTTPError, http.URLError) as e:
        return "Could not get recipe: {}".format(e)
    url = page.geturl()

    try:
        data = get_data(url)
    except ParseError as e:
        return "Could not parse recipe: {}".format(e)

    name = data["name"]
    return u"Try eating \x02{}!\x02 - {}".format(name, web.try_isgd(url))


@hook.command(autohelp=False)
def frecipe(inp):
    """frecipe - GET A FUCKING RECIPE!"""
    try:
        page = http.open(RANDOM_URL)
    except (http.HTTPError, http.URLError) as e:
        return "Could not get recipe: {}".format(e)
    url = page.geturl()

    try:
        data = get_data(url)
    except ParseError as e:
        return "Could not parse recipe: {}".format(e)

    name = data["name"].upper()
    text = random.choice(PHRASES).format(name)

    if CENSOR:
        text = text.replace("FUCK", "F**K")

    return u"{} - {}".format(text, web.try_isgd(url))