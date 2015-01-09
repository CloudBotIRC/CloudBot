from cloudbot.util import cleverbot
from cloudbot import hook


@hook.command("ask", "cleverbot", "cb")
def ask(text):
    """ <question> -- Asks Cleverbot <question> """
    session = cleverbot.Session()
    answer = session.ask(text)

    if answer.startswith("\n"):
        # cleverbot tried to advert us
        answer = session.ask(text)

    return answer
