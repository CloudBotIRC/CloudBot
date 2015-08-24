import socket

from mcstatus import MinecraftServer

from cloudbot import hook

mc_colors = [('\xa7f', '\x0300'), ('\xa70', '\x0301'), ('\xa71', '\x0302'), ('\xa72', '\x0303'),
             ('\xa7c', '\x0304'), ('\xa74', '\x0305'), ('\xa75', '\x0306'), ('\xa76', '\x0307'),
             ('\xa7e', '\x0308'), ('\xa7a', '\x0309'), ('\xa73', '\x0310'), ('\xa7b', '\x0311'),
             ('\xa71', '\x0312'), ('\xa7d', '\x0313'), ('\xa78', '\x0314'), ('\xa77', '\x0315'),
             ('\xa7l', '\x02'), ('\xa79', '\x0310'), ('\xa7o', ''), ('\xa7m', '\x13'),
             ('\xa7r', '\x0f'), ('\xa7n', '\x15')]


def format_colors(description):
    for original, replacement in mc_colors:
        description = description.replace(original, replacement)
    return description.replace("\xa7k", "")


@hook.command("mcping", "mcp")
def mcping(text):
    """<server[:port]> - gets info about the Minecraft server at <server[:port]>"""
    try:
        server = MinecraftServer.lookup(text)
    except (IOError, ValueError) as e:
        return e

    try:
        s = server.status()
    except socket.gaierror:
        return "Invalid hostname"
    except socket.timeout:
        return "Request timed out"
    except ConnectionRefusedError:
        return "Connection refused"
    except ConnectionError:
        return "Connection error"
    except (IOError, ValueError) as e:
        return "Error pinging server: {}".format(e)

    if isinstance(s.description, dict):
        description = format_colors(" ".join(s.description["text"].split()))
    else:
        description = format_colors(" ".join(s.description.split()))
        
    # I really hate people for putting colors IN THE VERSION
    # WTF REALLY THIS IS A THING NOW?

    if s.latency:
        return "{}\x0f - \x02{}\x0f - \x02{:.1f}ms\x02" \
            " - \x02{}/{}\x02 players".format(description, s.version.name_clean, s.latency,
                                              s.players.online, s.players.max).replace("\n", "\x0f - ")
    else:
        return "{}\x0f - \x02{}\x0f" \
            " - \x02{}/{}\x02 players".format(description, s.version.name_clean,
                                              s.players.online, s.players.max).replace("\n", "\x0f - ")
