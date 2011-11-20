
import socket
import struct


from util import hook

def get_info(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.send('\xfe')
        response = sock.recv(1)
        if response != '\xff':
            return "Server gave invalid response: "+repr(response)
        length = struct.unpack('!h', sock.recv(2))[0]
        values = sock.recv(length*2).decode('utf-16be').split(u'\xa7')
        sock.close()
        return "%s - %d/%d players" % (values[0], int(values[1]), int(values[2]))
    except:
        return "Error pinging "+host+":"+str(port)+", is it up? double-check your address!" 

@hook.command
def mcping(inp):
    ".mcping server[:port] - ping a minecraft server and show response."
    inp = inp.strip().split(" ")[0]

    if ":" in inp:
        host, port = inp.split(":", 1)
        try:
            port = int(port)
        except:
            return "Invalid port!"
    else:
        host = inp
        port = 25565
    return get_info(host, port)
