from util import hook
from util import http
import string
import socket
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
def mcstatus(inp, bot=None):
    ".mcstatus -- Checks the status of Minecraft's login servers."
    username = bot.config.get("api_keys", {}).get("mc_user", None)
    password = bot.config.get("api_keys", {}).get("mc_pass", None)
    if password is None:
        return "error: no login set"

    login = http.get("https://login.minecraft.net/?user="\
    + username + "&password=" + password + "&version=13")
    if username.lower() in login.lower():
        return "Minecraft login servers appear to be online!"
    else:
        return "Minecraft login servers appear to be offline!"


@hook.command
def mclogin(inp, say=None):
    ".mclogin <username> <password> -- Attempts to log in to Minecraft with "\
    " <username> and <password> (This is NOT logged)."
    inp = inp.split(" ")
    username = inp[0]
    password = inp[1]
    say("Attempting to log in using " + username)
    login = http.get("https://login.minecraft.net/?user="\
    + username + "&password=" + password + "&version=13")
    if username.lower() in login.lower():
        return "I logged in with " + username
    else:
        return "I couldn't log in using " + username + ", either"\
        " the password is wrong or Minecraft login servers are down!"


@hook.command
def mcpaid(inp):
    ".mcpaid <username> -- Checks if <username> has a "\
    "premium Minecraft account."
    login = http.get("http://www.minecraft.net/haspaid.jsp?user=" + inp)
    if "true" in login:
        return "The account \'" + inp + "\' is a "\
        "premium Minecraft account!"
    else:
        return "The account \'" + inp + "\' is not a "\
        "premium Minecraft account!"

from util import hook


@hook.command
def mcping(inp):
    ".mcping <server>[:port] - Ping a Minecraft server to check status."
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
