from util import hook, http
import socket
import struct

try:
    import DNS 
    # Please remember to install the dependancy 'pydns'
    pydns_installed = True
except ImportError:
    pydns_installed = False

def format_motd(motd):
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


def srvData(domain):
    DNS.ParseResolvConf()
    srv_req = DNS.Request(qtype='srv')
    srv_result = srv_req.req('_minecraft._tcp.{}'.format(domain))

    for getsrv in srv_result.answers:
        if getsrv['typename'] == 'SRV':
            data = [getsrv['data'][2],getsrv['data'][3]]
            return data


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
        return format_motd(mcping_connect(host, port))

    else:
        host = inp
        port = 25565
        rdata = format_motd(mcping_connect(host, port))

        if 'is it up' in rdata:
            if pydns_installed:
                getdata = srvData(inp)
                try:
                    host = str(getdata[1])
                    port = int(getdata[0])
                    return format_motd(mcping_connect(host, port))
                except: 
                    return "Error pinging %s, is it up? Double-check your address!" % inp
            else:
                return "Error pinging %s, is it up? Double-check your address!" % inp
        else:
            return rdata
