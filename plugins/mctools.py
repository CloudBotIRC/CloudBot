from util import hook, http
import socket
import json
import struct

def mccolorconvert(motd):
    empty = ""
    colors = [u"\x0300,\xa7f", u"\x0301,\xa70", u"\x0302,\xa71", u"\x0303,\xa72", u"\x0304,\xa7c", u"\x0305,\xa74", u"\x0306,\xa75", u"\x0307,\xa76", u"\x0308,\xa7e", u"\x0309,\xa7a", u"\x0310,\xa73", u"\x0311,\xa7b", u"\x0312,\xa71", u"\x0313,\xa7d", u"\x0314,\xa78", u"\x0315,\xa77", u"\x02,\xa7l", u"\x0310,\xa79", u"\x09,\xa7o", u"\x13,\xa7m", u"\x0f,\xa7r", u"\x15,\xa7n"];
    for s in colors:
        lcol = s.split(",")
        motd = motd.replace(lcol[1], lcol[0])
    motd = motd.replace(u"\xa7k", empty)
    return motd

def mcping_connect(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.send('\xfe\x01')
        response = sock.recv(1)
        print response

        if response[0] != '\xff':
            return "Server gave invalid response: " + repr(response)
        length = struct.unpack('!h', sock.recv(2))[0]

        values = sock.recv(length * 2).decode('utf-16be')

        data = values.split(u'\x00')  # try to decode data using new format
        if len(data) == 1:
            # failed to decode data, server is using old format
            data = values.split(u'\xa7')
            message = u"{} - {}/{} players".format(data[0], data[1], data[2])
        else:
            # decoded data, server is using new format
            message = u"{} \x0f- {} - {}/{} players".format(data[3], data[2], data[4], data[5])

        sock.close()
        return message

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
    return mccolorconvert(mcping_connect(host, port))

