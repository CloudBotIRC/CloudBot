from cloudbot.util import cleverbot
from cloudbot import hook

import urllib


@hook.command("ask", "cleverbot", "cb")
def ask(text):
    """ <question> -- Asks Cleverbot <question> """
    session = cleverbot.Session()

    try:
        answer = session.ask(text)
        while answer.startswith("\n"):
            # cleverbot tried to advert us
            answer = session.ask(text)
    except urllib.error.HTTPError:
        return "Could not get response. Cleverbot is angry :("

    return answer
