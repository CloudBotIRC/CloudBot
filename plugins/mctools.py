from util import hook, http
import socket
import json
import struct


def mcping_connect(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.send('\xfe\x01')
        response = sock.recv(1)

        if response[0] != '\xff':
            return "Server gave invalid response: " + repr(response)
        length = struct.unpack('!h', sock.recv(2))[0]
        values = sock.recv(length * 2).decode('utf-16be').split(u'\x00')

        sock.close()
        return u"{} - Minecraft {} - {}/{} players".format(values[3], values[2], values[4], values[5])
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
    "mcstatus -- Checks the status of various Mojang (the creators of Minecraft) servers."

    try:
        request = http.get("http://status.mojang.com/check")
    except (http.URLError, http.HTTPError) as e:
        return "Unable to get Minecraft server status: {}".format(e)

    # change the json from a list of dictionaies to a dictionary
    data = json.loads(request.replace("}", "").replace("{", "").replace("]", "}").replace("[", "{"))

    out = []
    # use a loop so we don't have to update it if they add more servers
    for server, status in data.items():
        if status == "green":
            out.append("{} is \x033\x02online\x02\x03".format(server))
        else:
            out.append("{} is \x034\x02offline\x02\x03".format(server))

    return ", ".join(out) + "."


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
