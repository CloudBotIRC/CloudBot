from cloudbot.util import cleverbot
from cloudbot import hook

import urllib


@hook.command("ask", "cleverbot", "cb")
def ask(text):
    """ <question> -- Asks Cleverbot <question> """
    session = cleverbot.Session()
    attempt = 0

    try:
        answer = session.ask(text)
        while answer.startswith("\n") and attempt < 3:
            # Cleverbot tried to advert us
            answer = session.ask(text)
            attempt += 1
    except urllib.error.HTTPError:
        return "Could not get response. Cleverbot is angry :("

    return answer
