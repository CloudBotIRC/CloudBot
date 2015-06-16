"""
cypher.py

Ciphers and deciphers strings.

Created By:
    - Tom <https://github.com/instanceoftom>

Modified By:
    - Fletcher Boyd <https://github.com/thenoodle68>
    - Dabo Ross <https://github.com/daboross>
    - Luke Rogers <https://github.com/lukeroge>

License:
    GPL v3
"""

import base64
import binascii

from cloudbot import hook


def encode(password, text):
    """
    :type password: str
    :type text: str
    """
    enc = []
    for i in range(len(text)):
        key_c = password[i % len(password)]
        enc_c = chr((ord(text[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()


def decode(password, encoded, notice):
    """
    :type password: str
    :type encoded: str
    """
    dec = []
    try:
        encoded_bytes = base64.urlsafe_b64decode(encoded.encode()).decode()
    except binascii.Error:
        notice("Invalid input '{}'".format(encoded))
        return
    for i in range(len(encoded_bytes)):
        key_c = password[i % len(password)]
        dec_c = chr((256 + ord(encoded_bytes[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


@hook.command("cypher", "cipher")
def cypher(text, notice):
    """<pass> <string> -- cyphers <string> with <password>"""
    split = text.split(None, 1)
    if len(split) < 2:
        notice(cypher.__doc__)
        return
    password = split[0]
    plaintext = split[1]
    return encode(password, plaintext)


@hook.command("decypher", "decipher")
def decypher(text, notice):
    """<pass> <string> - decyphers <string> with <password>"""
    split = text.split(None, 1)
    if len(split) < 2:
        notice(decypher.__doc__)
        return
    password = split[0]
    encoded = split[1]
    return decode(password, encoded, notice)
