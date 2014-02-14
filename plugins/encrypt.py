import os
import base64
import json
import hashlib

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

from util import hook


# helper functions to pad and unpad a string to a specified block size
# <http://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256>
BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]

# helper functions to encrypt and encode a string with AES and base64
encode_aes = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
decode_aes = lambda c, s: unpad(c.decrypt(base64.b64decode(s)))

db_ready = False


def db_init(db):
    """check to see that our db has the the encryption table."""
    global db_ready
    if not db_ready:
        db.execute("create table if not exists encryption(encrypted, iv, "
                   "primary key(encrypted))")
        db.commit()
        db_ready = True


def get_salt(bot):
    """generate an encryption salt if none exists, then returns the salt"""
    if not bot.config.get("random_salt", False):
        bot.config["random_salt"] = hashlib.md5(os.urandom(16)).hexdigest()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    return bot.config["random_salt"]


@hook.command
def encrypt(inp, bot=None, db=None, notice=None):
    """encrypt <pass> <string> -- Encrypts <string> with <pass>. (<string> can only be decrypted using this bot)"""
    db_init(db)

    split = inp.split(" ")

    # if there is only one argument, return the help message
    if len(split) == 1:
        notice(encrypt.__doc__)
        return

    # generate the key from the password and salt
    password = split[0]
    salt = get_salt(bot)
    key = PBKDF2(password, salt)

    # generate the IV and encode it to store in the database
    iv = Random.new().read(AES.block_size)
    iv_encoded = base64.b64encode(iv)

    # create the AES cipher and encrypt/encode the text with it
    text = " ".join(split[1:])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encoded = encode_aes(cipher, text)

    # store the encoded text and IV in the DB for decoding later
    db.execute("insert or replace into encryption(encrypted, iv)"
               "values(?,?)", (encoded, iv_encoded))
    db.commit()

    return encoded


@hook.command
def decrypt(inp, bot=None, db=None, notice=None):
    """decrypt <pass> <string> -- Decrypts <string> with <pass>. (can only decrypt strings encrypted on this bot)"""
    if not db_ready:
        db_init(db)

    split = inp.split(" ")

    # if there is only one argument, return the help message
    if len(split) == 1:
        notice(decrypt.__doc__)
        return

    # generate the key from the password and salt
    password = split[0]
    salt = get_salt(bot)
    key = PBKDF2(password, salt)

    text = " ".join(split[1:])

    # get the encoded IV from the database and decode it
    iv_encoded = db.execute("select iv from encryption where"
                            " encrypted=?", (text,)).fetchone()[0]
    iv = base64.b64decode(iv_encoded)

    # create AES cipher, decode text, decrypt text, and unpad it
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return decode_aes(cipher, text)
