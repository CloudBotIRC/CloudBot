from cloudbot.util import cleverbot
from cloudbot import hook


@hook.command
def ask(text):
    cb = cleverbot.Session()
    data = cb.Ask(text)
    return data
