import random

from cloudbot import hook
from cloudbot.util import http, web

types=['trivia', 'math', 'date', 'year']

@hook.command(autohelp=False)
def fact():
    """Gets a random fact about numbers or dates."""
    fact_type = random.choice(types)
    attempts = 0
    while True:
        try:
            json = http.get_json('http://numbersapi.com/random/{}?json'.format(fact_type))
        except:
            if attempts > 2:
                return "There was an error contacting the numbersapi.com API."
            else:
                attempts += 1
                continue
        response = json['text']
        return response 
