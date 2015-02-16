from cloudbot import hook
from cloudbot.util import http, web


@hook.command(autohelp=False)
def cats():
    """gets a fucking fact about cats."""
    
    attempts = 0
    while True:
        try:
            json = http.get_json('http://catfacts-api.appspot.com/api/facts?number=1')
        except:
            if attempts > 2:
                return "There was an error contacting the API."
            else:
                attempts += 1
                continue
        response = json['facts']
        return response 
