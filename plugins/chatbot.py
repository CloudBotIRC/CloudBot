from cloudbot.util import cleverbot
from cloudbot import hook

import urllib


@hook.command("ask", "cleverbot", "cb")
def ask(text):
    """ <question> -- Asks Cleverbot <question> """
    session = cleverbot.Session()
    timeout = 0

    try:
        answer = session.ask(text)
        while answer.startswith("\n") and timeout < 3:
            # cleverbot tried to advert us
            answer = session.ask(text)
            timeout += 1
    except urllib.error.HTTPError:
        return "Could not get response. Cleverbot is angry :("

    return answer
