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
    yes = []
    no = []
    for server, status in data.items():
        if status == "green":
            yes.append(server)
        else:
            no.append(server)
    if yes:
        out = "\x033\x02Online\x02\x0f: " + ", ".join(yes)
        if no:
            out += " "
    if no:
        out += "\x034\x02Offline\x02\x0f: " + ", ".join(no)

    return "\x0f" + out.replace(".mojang.com", ".mj") \
                       .replace(".minecraft.net", ".mc")
