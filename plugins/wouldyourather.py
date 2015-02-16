from cloudbot import hook
from cloudbot.util import http, web


@hook.command("wyr", autohelp=False)
def wouldyourather():
    """Asks a would you rather question"""
    
    attempts = 0
    while True:
        try:
            json = http.get_json('http://rrrather.com/botapi')
        except:
            if attempts > 2:
                return "There was an error contacting the rrrather.com API."
            else:
                attempts += 1
                continue
        response = "{}: {} \x02OR\x0F {}?".format(json['title'], json['choicea'], json['choiceb'])
        return response 
