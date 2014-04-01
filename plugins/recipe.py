from util import hook, http, web

METADATA_URL = "http://omnidator.appspot.com/microdata/json/?url={}"
RANDOM_URL = "http://www.cookstr.com/searches/surprise"

clean_key = lambda i: i.split("#")[1]


def get_data(url):
    """ Uses the omnidator API to parse the metadata from the provided URL """
    omni = http.get_json(METADATA_URL.format(url))
    schemas = omni["@"]
    for d in schemas:
        if d["a"] == "<http://schema.org/Recipe>":
            data = {clean_key(key): value for (key, value) in d.iteritems()
                    if key.startswith("http://schema.org/Recipe")}
            return data


@hook.command(autohelp=False)
def recipe(inp):
    """recipe - Gets a random recipe from cookstr.com!"""
    page = http.open(RANDOM_URL)
    url = page.geturl()

    data = get_data(url)
    name = data["name"]
    return u"Try eating \x02{}!\x02 - {}".format(name, web.try_isgd(url))