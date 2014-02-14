import json

from util import hook, textgen


def get_generator(_json, variables):
    data = json.loads(_json)
    return textgen.TextGenerator(data["templates"],
                                 data["parts"], variables=variables)


@hook.command
def kill(inp, action=None, nick=None, conn=None, notice=None):
    """kill <user> -- Makes the bot kill <user>."""
    target = inp.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot kill itself, kill them
    if target.lower() == conn.nick.lower() or target.lower() == "itself":
        target = nick

    variables = {
        "user": target
    }

    with open("plugins/data/kills.json") as f:
        generator = get_generator(f.read(), variables)

    # act out the message
    action(generator.generate_string())
