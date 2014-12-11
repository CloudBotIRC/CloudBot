import socket
import struct
import json
import traceback

from cloudbot import hook

try:
    import DNS
except ImportError:
    DNS = None

mc_colors = [('\xa7f', '\x0300'), ('\xa70', '\x0301'), ('\xa71', '\x0302'), ('\xa72', '\x0303'),
             ('\xa7c', '\x0304'), ('\xa74', '\x0305'), ('\xa75', '\x0306'), ('\xa76', '\x0307'),
             ('\xa7e', '\x0308'), ('\xa7a', '\x0309'), ('\xa73', '\x0310'), ('\xa7b', '\x0311'),
             ('\xa71', '\x0312'), ('\xa7d', '\x0313'), ('\xa78', '\x0314'), ('\xa77', '\x0315'),
             ('\xa7l', '\x02'), ('\xa79', '\x0310'), ('\xa7o', '\t'), ('\xa7m', '\x13'),
             ('\xa7r', '\x0f'), ('\xa7n', '\x15')]


# EXCEPTIONS
class PingError(Exception):
    pass


class ParseError(Exception):
    pass


# MISC
def unpack_varint(s):
    d = 0
    i = 0
    while True:
        b = ord(s.recv(1))
        d |= (b & 0x7F) << 7 * i
        i += 1
        if not b & 0x80:
            return d


pack_data = lambda d: struct.pack('>b', len(d)) + d
pack_port = lambda i: struct.pack('>H', i)

# DATA FUNCTIONS


def mcping_modern(host, port):
    """ pings a server using the modern (1.7+) protocol and returns data """
    try:
        # connect to the server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.connect((host, port))
        except socket.gaierror:
            raise PingError("Invalid hostname")
        except socket.timeout:
            raise PingError("Request timed out")
        except ConnectionRefusedError:
            raise PingError("Connection refused")
        except ConnectionError:
            raise PingError("Connection error")

        # send handshake + status request
        s.send(pack_data(b"\x00\x00" + pack_data(host.encode('utf8')) + pack_port(port) + b"\x01"))
        s.send(pack_data(b"\x00"))

        # read response
        unpack_varint(s)  # Packet length
        unpack_varint(s)  # Packet ID
        l = unpack_varint(s)  # String length

        if not l > 1:
            raise PingError("Invalid response")

        d = b""
        while len(d) < l:
            d += s.recv(1024)

        # Close our socket
        s.close()
    except socket.error:
        raise PingError("Socket Error")

    # Load json and return
    data = json.loads(d.decode('utf8'))
    try:
        version = data["version"]["name"]
        try:
            desc = " ".join(data["description"]["text"].split())
        except TypeError:
            desc = " ".join(data["description"].split())
        max_players = data["players"]["max"]
        online = data["players"]["online"]
    except Exception as e:
        # TODO: except Exception is bad
        traceback.print_exc(e)
        raise PingError("Unknown Error: {}".format(e))

    output = {
        "motd": format_colors(desc),
        "motd_raw": desc,
        "version": version,
        "players": online,
        "players_max": max_players
    }
    return output


def mcping_legacy(host, port):
    """ pings a server using the legacy (1.6 and older) protocol and returns data """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((host, port))
        sock.send(b'\xfe\x01')
        response = sock.recv(1)
    except socket.gaierror:
        raise PingError("Invalid hostname")
    except socket.timeout:
        raise PingError("Request timed out")
    except ConnectionRefusedError:
        raise PingError("Connection refused")
    except ConnectionError:
        raise PingError("Connection error")

    if response[0] != '\xff':
        raise PingError("Invalid response")

    length = struct.unpack('!h', sock.recv(2))[0]
    values = sock.recv(length * 2).decode('utf-16be')
    data = values.split('\x00')  # try to decode data using new format
    if len(data) == 1:
        # failed to decode data, server is using old format
        data = values.split('\xa7')
        output = {
            "motd": format_colors(" ".join(data[0].split())),
            "motd_raw": data[0],
            "version": None,
            "players": data[1],
            "players_max": data[2]
        }
    else:
        # decoded data, server is using new format
        output = {
            "motd": format_colors(" ".join(data[3].split())),
            "motd_raw": data[3],
            "version": data[2],
            "players": data[4],
            "players_max": data[5]
        }
    sock.close()
    return output


# FORMATTING/PARSING FUNCTIONS

def check_srv(domain):
    """ takes a domain and finds minecraft SRV records """
    DNS.DiscoverNameServers()
    srv_req = DNS.Request(qtype='srv')
    srv_result = srv_req.req('_minecraft._tcp.{}'.format(domain))

    for getsrv in srv_result.answers:
        if getsrv['typename'] == 'SRV':
            data = [getsrv['data'][2], getsrv['data'][3]]
            return data


def parse_input(inp):
    """ takes the input from the mcping command and returns the host and port """
    inp = inp.strip().split(" ")[0]
    if ":" in inp:
        # the port is defined in the input string
        host, port = inp.split(":", 1)
        try:
            port = int(port)
            if port > 65535 or port < 0:
                raise ParseError("The port '{}' is invalid.".format(port))
        except ValueError:
            raise ParseError("The port '{}' is invalid.".format(port))
        return host, port
    if DNS is not None:
        # the port is not in the input string, but we have PyDNS so look for a SRV record
        srv_data = check_srv(inp)
        if srv_data:
            return str(srv_data[1]), int(srv_data[0])
    # return default port
    return inp, 25565


def format_colors(motd):
    for original, replacement in mc_colors:
        motd = motd.replace(original, replacement)
    motd = motd.replace("\xa7k", "")
    return motd


def format_output(data):
    if data["version"]:
        return "{motd}\x0f - {version}\x0f - {players}/{players_max}" \
               " players.".format(**data).replace("\n", "\x0f - ")
    else:
        return "{motd}\x0f - {players}/{players_max}" \
               " players.".format(**data).replace("\n", "\x0f - ")


@hook.command("mcping", "mcp")
def mcping(text):
    """<server[:port]> - gets the MOTD of the Minecraft server at <server[:port]>"""
    try:
        host, port = parse_input(text)
    except ParseError as e:
        return "Could not parse input ({})".format(e)

    try:
        data = mcping_modern(host, port)
    except PingError:
        try:
            data = mcping_legacy(host, port)
        except PingError as e:
            return "Could not ping server, is it offline? ({})".format(e)

    return format_output(data)
