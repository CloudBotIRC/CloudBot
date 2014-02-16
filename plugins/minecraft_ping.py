# TODO: Rewrite this whole mess
import socket
import struct
import json

from util import hook


try:
    import DNS
    # Please remember to install the dependency 'pydns'
    pydns_installed = True
except ImportError:
    pydns_installed = False


mccolors = [u"\x0300,\xa7f", u"\x0301,\xa70", u"\x0302,\xa71", u"\x0303,\xa72", u"\x0304,\xa7c", u"\x0305,\xa74",
            u"\x0306,\xa75", u"\x0307,\xa76", u"\x0308,\xa7e", u"\x0309,\xa7a", u"\x0310,\xa73", u"\x0311,\xa7b",
            u"\x0312,\xa71", u"\x0313,\xa7d", u"\x0314,\xa78", u"\x0315,\xa77", u"\x02,\xa7l", u"\x0310,\xa79",
            u"\x09,\xa7o", u"\x13,\xa7m", u"\x0f,\xa7r", u"\x15,\xa7n"]


def mc_color_format(motd):
    for colorcombo in mccolors:
        colorarray = colorcombo.split(",")
        motd = motd.replace(colorarray[1], colorarray[0])
    motd = motd.replace(u"\xa7k", "")
    return motd


def unpack_varint(s):
    d = 0
    i = 0
    while True:
        b = ord(s.recv(1))
        d |= (b & 0x7F) << 7 * i
        i += 1
        if not b & 0x80:
            return d


def pack_data(d):
    return struct.pack('>b', len(d)) + d


def pack_port(i):
    return struct.pack('>H', i)


def mcping_modern(host, port):
    """ pings a server using the modern (1.7+) protocol and returns formatted output """
    # connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # send handshake + status request
    s.send(pack_data("\x00\x00" + pack_data(host.encode('utf8')) + pack_port(port) + "\x01"))
    s.send(pack_data("\x00"))

    # read response
    unpack_varint(s)      # Packet length
    unpack_varint(s)      # Packet ID
    l = unpack_varint(s)  # String length

    if not l > 1:
        raise Exception

    d = ""
    while len(d) < l:
        d += s.recv(1024)

    # Close our socket
    s.close()

    # Load json and return
    data = json.loads(d.decode('utf8'))
    try:
        version = data["version"]["name"]
        if data["description"].get("text", None):
            desc = u" ".join(data["description"]["text"].split())
        else:
            desc = u" ".join(data["description"].split())
        max_players = data["players"]["max"]
        online = data["players"]["online"]
    except Exception as e:
        from pprint import pprint
        pprint(data)
        return "Invalid data - check console ({})".format(e)
    return mc_color_format(u"{}\x0f - {}\x0f - {}/{} players.".format(desc, version, online,
                                                                      max_players)).replace("\n", u"\x0f - ")


def mcping_legacy(host, port):
    """ pings a server using the legacy (1.6 and older) protocol and returns formatted output """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        message = u"{} - {}/{} players".format(mc_color_format(data[0]), data[1], data[2])
    else:
        # decoded data, server is using new format
        message = u"{} \x0f- {} - {}/{} players".format(mc_color_format(data[3]),
                                                        mc_color_format(data[2]), data[4], data[5])
    sock.close()
    return message


def get_srv_data(domain):
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
        host, port = inp.split(":", 1)
        try:
            port = int(port)
        except:
            raise Exception("The port '{}' is invalid.".format(port))
        return host, port
    if pydns_installed:
        srv_data = get_srv_data(inp)
        if srv_data:
            return str(srv_data[1]), int(srv_data[0])
    return inp, 25565


@hook.command
@hook.command("mcp6")
def mcping6(inp):
    """mcping6 <server>[:port] - Ping a Minecraft server version 1.6 or smaller to check status."""
    #try:
    host, port = parse_input(inp)
    #except Exception as ex:
     #   return ex.args[0]
    try:
        return mcping_legacy(host, port)
    except:
        return "The 1.6 server {}:{} looks offline from here.".format(host, port)


@hook.command
@hook.command("mcp7")
def mcping7(inp):
    """mcping <server>[:port] - Ping a Minecraft server version 1.7 or greater to check status."""
    try:
        host, port = parse_input(inp)
    except Exception as ex:
        return ex.args[0]
    try:
        return mcping_modern(host, port)
    except:
        return "The 1.7 server {}:{} looks offline from here.".format(host, port)


@hook.command
@hook.command("mcp")
def mcping(inp):
    """mcping <server>[:port] - Ping a Minecraft server to check status."""
  #  try:
    host, port = parse_input(inp)
    #except Exception as e:
     #   return e.args[0]
#

    try:
        return mcping_modern(host, port)
    except:
        try:
            return mcping_legacy(host, port)
        except:
            return "The server {} ({}:{}) looks offline from here.".format(inp, host, port)
