import json

from util import hook, http


@hook.command(autohelp=False)
def mcstatus(inp):
    """mcstatus -- Checks the status of various Mojang (the creators of Minecraft) servers."""

    try:
        request = http.get("http://status.mojang.com/check")
    except (http.URLError, http.HTTPError) as e:
        return "Unable to get Minecraft server status: {}".format(e)

    # lets just reformat this data to get in a nice format
    data = json.loads(request.replace("}", "").replace("{", "").replace("]", "}").replace("[", "{"))

    out = []

    # use a loop so we don't have to update it if they add more servers
    green = []
    yellow = []
    red = []
    for server, status in data.items():
        if status == "green":
            green.append(server)
        elif status == "yellow":
            yellow.append(server)
        else:
            red.append(server)

    if green:
        out = "\x033\x02Online\x02\x0f: " + ", ".join(green)
        if yellow:
            out += " "
    if yellow:
        out += "\x02Issues\x02: " + ", ".join(yellow)
        if red:
            out += " "
    if red:
        out += "\x034\x02Offline\x02\x0f: " + ", ".join(red)

    return "\x0f" + out.replace(".mojang.com", ".mj") \
                       .replace(".minecraft.net", ".mc")
