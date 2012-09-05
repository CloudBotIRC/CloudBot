from util import hook
from util import http
from util.text import get_text_list
import string
import socket
import json
import struct


def mcping_connect(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.send('\xfe')
        response = sock.recv(1)
        if response != '\xff':
            return "Server gave invalid response: " + repr(response)
        length = struct.unpack('!h', sock.recv(2))[0]
        values = sock.recv(length * 2).decode('utf-16be').split(u'\xa7')
        sock.close()
        return "%s - %d/%d players"\
        % (values[0], int(values[1]), int(values[2]))
    except:
        return "Error pinging " + host + ":" + str(port) +\
        ", is it up? Double-check your address!"


@hook.command(autohelp=False)
def mclogin(inp, bot=None):
    "mclogin -- Checks the status of Minecraft's login servers."
    username = bot.config.get("api_keys", {}).get("mc_user", None)
    password = bot.config.get("api_keys", {}).get("mc_pass", None)
    if password is None:
        return "error: no login set"

    login = http.get("https://login.minecraft.net/", user=username,
                     password=password, version=13)

    if username.lower() in login.lower():
        return "Minecraft login servers appear to be online!"
    else:
        return "Minecraft login servers appear to be offline!"


@hook.command(autohelp=False)
def mcstatus(inp, say=None):
    "mcstatus -- Checks the status various Mojang servers."

    try:
        request = http.get("http://status.mojang.com/check")
    except (http.URLError, http.HTTPError) as e:
        return "Unable to get minecraft server status: %s" % e

    # change the json from a list of dictionaies to a dictionary
    data = json.loads(request.replace("}", "").replace("{", "").replace("]", "}").replace("[", "{"))

    # check if skins are online
    try:
        request = http.get("http://s3.amazonaws.com/MinecraftSkins/Shnaw.png")
        data["minecraft skin server"] = "green"
    except (http.URLError, http.HTTPError) as e:
        data["minecraft skin server"] = "red"

    out = []
    # use a loop so we don't have to update it if they add more servers
    for server, status in data.items():
        if status == "green":
            out.append("%s is \x033\x02online\x02\x03" % server)
        else:
            out.append("%s is \x034\x02offline\x02\x03" % server)

    return ", ".join(out) + "."


@hook.command("haspaid")
@hook.command
def mcpaid(inp):
    "mcpaid <username> -- Checks if <username> has a premium Minecraft account."
    login = http.get("http://www.minecraft.net/haspaid.jsp", user=inp)

    if "true" in login:
        return 'The account "%s" is a premium Minecraft account!' % inp
    else:
        return 'The account "%s" is not a premium Minecraft account!' % inp


@hook.command
def mcping(inp):
    "mcping <server>[:port] - Ping a Minecraft server to check status."
    inp = inp.strip().split(" ")[0]

    if ":" in inp:
        host, port = inp.split(":", 1)
        try:
            port = int(port)
        except:
            return "error: invalid port!"
    else:
        host = inp
        port = 25565
    return mcping_connect(host, port)
