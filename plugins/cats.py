import requests
from cloudbot import hook


@hook.command(autohelp=False)
def cats():
    """gets a fucking fact about cats."""

    attempts = 0
    while True:
        try:
            r = requests.get(
                'http://catfacts-api.appspot.com/api/facts?number=1')
        except:
            if attempts > 2:
                return "There was an error contacting the API."
            else:
                attempts += 1
                continue
        json = r.json()
        response = json['facts']
        return response

@hook.command(autohelp=False)
def catgifs():
    """gets a fucking cat gif."""
    attempts = 0
    while True:
        try:
            r = requests.get("http://marume.herokuapp.com/random.gif")

        except:
            if attempts > 2:
                return "there was an error finding a cat gif for you."
            else:
                attempts += 1
                continue
        response = r.url
        return "OMG A CAT GIF: {}".format(response)
