import random
import microdata
import requests

from cloudbot import hook, http, web


base_url = "http://www.cookstr.com"
search_url = base_url + "/searches"
random_url = search_url + "/surprise"

# set this to true to censor this plugin!
censor = True
phrases = [
    "EAT SOME FUCKING \x02{}\x02",
    "YOU WON'T NOT MAKE SOME FUCKING \x02{}\x02",
    "HOW ABOUT SOME FUCKING \x02{}?\x02",
    "WHY DON'T YOU EAT SOME FUCKING \x02{}?\x02",
    "MAKE SOME FUCKING \x02{}\x02",
    "INDUCE FOOD COMA WITH SOME FUCKING \x02{}\x02"
]

clean_key = lambda i: i.split("#")[1]


class ParseError(Exception):
    pass


def get_data(url):
    """ Uses the metadata module to parse the metadata from the provided URL """
    try:
        request = requests.get(url)
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise ParseError(e)

    items = microdata.get_items(request.text)

    for item in items:
        if item.itemtype == [microdata.URI("http://schema.org/Recipe")]:
            return item

    raise ParseError("No recipe data found")


@hook.command(autohelp=False)
def recipe(text):
    """[term] - gets a recipe for [term], or gets a random recipe if no term is specified"""
    if text:
        # get the recipe URL by searching
        try:
            search = http.get_soup(search_url, query=text.strip())
        except (http.HTTPError, http.URLError) as e:
            return "Could not get recipe: {}".format(e)

        # find the list of results
        result_list = search.find('div', {'class': 'found_results'})

        if result_list:
            results = result_list.find_all('div', {'class': 'recipe_result'})
        else:
            return "No results"

        # pick a random front page result
        result = random.choice(results)

        # extract the URL from the result
        url = base_url + result.find('div', {'class': 'image-wrapper'}).find('a')['href']

    else:
        # get a random recipe URL
        try:
            page = http.open(random_url)
        except (http.HTTPError, http.URLError) as e:
            return "Could not get recipe: {}".format(e)
        url = page.geturl()

    # use get_data() to get the recipe info from the URL
    try:
        data = get_data(url)
    except ParseError as e:
        return "Could not parse recipe: {}".format(e)

    name = data.name.strip()
    return "Try eating \x02{}!\x02 - {}".format(name, web.try_shorten(url))


@hook.command(autohelp=False)
def dinner():
    """- TELLS YOU WHAT THE F**K YOU SHOULD MAKE FOR DINNER"""
    try:
        page = http.open(random_url)
    except (http.HTTPError, http.URLError) as e:
        return "Could not get recipe: {}".format(e)
    url = page.geturl()

    try:
        data = get_data(url)
    except ParseError as e:
        return "Could not parse recipe: {}".format(e)

    name = data.name.strip().upper()
    text = random.choice(phrases).format(name)

    if censor:
        text = text.replace("FUCK", "F**K")

    return "{} - {}".format(text, web.try_shorten(url))
