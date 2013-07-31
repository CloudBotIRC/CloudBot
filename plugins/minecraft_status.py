from util import hook, http
import json


@hook.command(autohelp=False)
def mcstatus(inp, say=None):
    "mcstatus -- Checks the status of various Mojang (the creators of Minecraft) servers."

    try:
        request = http.get("http://status.mojang.com/check")
    except (http.URLError, http.HTTPError) as e:
        return "Unable to get Minecraft server status: {}".format(e)

    # lets just reformat this data to get in a nice format
    data = json.loads(request.replace("}", "").replace("{", "").replace("]", "}").replace("[", "{"))

    out = []
    # use a loop so we don't have to update it if they add more servers
    for server, status in data.items():
        if status == "green":
            out.append("{} is \x033\x02online\x02\x0f".format(server))
        else:
            out.append("{} is \x034\x02offline\x02\x0f".format(server))

    return "\x0f" + ", ".join(out) + "."


@hook.command("haspaid")
@hook.command
def mcpaid(inp):
    "mcpaid <username> -- Checks if <username> has a premium Minecraft account."

    user = inp.strip()

    try:
        status = http.get("http://www.minecraft.net/haspaid.jsp", user=user)
    except (http.URLError, http.HTTPError) as e:
        return "Unable to get user registration status: {}".format(e)

    if "true" in status:
        return 'The account "{}" is a premium Minecraft account!'.format(inp)
    else:
        return 'The account "{}" is not a premium Minecraft account!'.format(inp)
