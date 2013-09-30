from util import hook
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

import os
import base64
import json
import hashlib

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[0:-ord(s[-1])]


def get_salt(bot):
	if not bot.config.get("random_salt", False):
		bot.config["random_salt"] = hashlib.md5(os.urandom(16)).hexdigest()
		json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
	return bot.config["random_salt"]


@hook.command
def encrypt(inp, bot=None):
    """encrypt <pass> <string> -- Encrypts <string> with <pass>."""
    password = inp.split(" ")[0]
    salt = get_salt(bot)
    key = PBKDF2(password, salt)

    text = " ".join(inp.split(" ")[1:])
    cipher = AES.new(key, AES.MODE_ECB) # never use ECB in strong systems obviously
    return base64.b64encode(cipher.encrypt(pad(text)))


@hook.command
def decrypt(inp, bot=None):
    """decrypt <pass> <string> -- Decrypts <string> with <pass>."""
    password = inp.split(" ")[0]
    salt = get_salt(bot)
    key = PBKDF2(password, salt)

    text = " ".join(inp.split(" ")[1:])
    cipher = AES.new(key, AES.MODE_ECB) # never use ECB in strong systems obviously
    return unpad(cipher.decrypt(base64.b64decode(text)))