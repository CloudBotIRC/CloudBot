import asyncio
import json

from cloudbot import hook, textgen


def get_generator(_json, variables):
    data = json.loads(_json)
    return textgen.TextGenerator(data["templates"],
                                 data["parts"], variables=variables)


@asyncio.coroutine
@hook.command()
def kill(text, action=None, nick=None, conn=None, notice=None):
    """kill <user> -- Makes the bot kill <user>."""
    target = text.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot kill itself, kill them
    if target.lower() == conn.nick.lower() or target.lower() == "itself":
        target = nick

    variables = {
        "user": target
    }

    with open("./data/kills.json") as f:
        generator = get_generator(f.read(), variables)

    # act out the message
    action(generator.generate_string())
