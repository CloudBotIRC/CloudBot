import base64

from util import hook


def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc))


def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc.encode('ascii', 'ignore'))
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


@hook.command
def cypher(inp):
    """cypher <pass> <string> -- Cyphers <string> with <password>."""

    passwd = inp.split(" ")[0]
    inp = " ".join(inp.split(" ")[1:])
    return encode(passwd, inp)


@hook.command
def decypher(inp):
    """decypher <pass> <string> -- Decyphers <string> with <password>."""
    passwd = inp.split(" ")[0]
    inp = " ".join(inp.split(" ")[1:])
    return decode(passwd, inp)
