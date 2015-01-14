import json
import codecs
import os

from cloudbot import hook
from cloudbot.util import textgen


@hook.onload
def load_slaps(bot):
    global slaps
    with codecs.open(os.path.join(bot.data_dir, "kills.json"), encoding="utf-8") as f:
        slaps = json.load(f)


@hook.command
def slap(text, action, nick, conn, notice):
    """slap <user> -- Makes the bot slap <user>."""
    target = text.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot slap itself, slap them
    if target.lower() == conn.nick.lower() or target.lower() == "itself":
        target = nick

    variables = {
        "user": target
    }
    generator = textgen.TextGenerator(slaps["templates"], slaps["parts"], variables=variables)

    # act out the message
    action(generator.generate_string())
