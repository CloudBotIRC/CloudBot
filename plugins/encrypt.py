import os
import base64
import hashlib
import asyncio
import traceback

# noinspection PyUnresolvedReferences
from pbkdf2 import PBKDF2
# noinspection PyUnresolvedReferences
from Crypto import Random
# noinspection PyUnresolvedReferences
from Crypto.Cipher import AES

from cloudbot import hook

BS = AES.block_size

# helper functions to pad and un-pad a string to a specified block size
# <http://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256>


def pad(s):
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)


def unpad(s):
    return s[0:-ord(s[-1])]


# helper functions to encrypt and encode a string with AES and base64

def encode_aes(c, s):
    return base64.b64encode(c.encrypt(pad(s)))


def decode_aes(c, s):
    decoded = c.decrypt(base64.b64decode(s))
    try:
        return unpad(decoded.decode())
    except UnicodeDecodeError:
        print("Failed to encode an encrypted message result as UTF-8")
        traceback.print_exc()
        # This usually happens if password is invalid
        return "Invalid password for the given message (couldn't encode result as utf-8)"


@hook.on_start
def create_db(db):
    """check to see that our db has the the encryption table.
    :type db: sqlalchemy.orm.session.Session
    """
    db.execute("create table if not exists encryption(encrypted, iv, "
               "primary key(encrypted))")
    db.commit()


def get_salt(bot):
    """generate an encryption salt if none exists, then returns the salt
    :type bot: cloudbot.bot.CloudBot
    """
    if not bot.config.get("random_salt", False):
        bot.config["random_salt"] = hashlib.md5(os.urandom(16)).hexdigest()
        bot.config.save_config()
    return bot.config.get("random_salt")


@asyncio.coroutine
@hook.command
def encrypt(text, bot, db, notice):
    """<pass> <string> - encrypts <string> with <pass>. (<string> can only be decrypted using this bot)
    :type text: str
    :type bot: cloudbot.bot.CloudBot
    :type db: sqlalchemy.orm.session.Session
    """

    text_split = text.split(" ")

    # if there is only one argument, return the help message
    if len(text_split) == 1:
        notice(encrypt.__doc__)
        return

    # generate the key from the password and salt
    password = text_split[0]
    salt = get_salt(bot)
    key = PBKDF2(password, salt).read(32)

    # generate the IV and encode it to store in the database
    iv = Random.new().read(AES.block_size)
    iv_encoded = base64.b64encode(iv)

    # create the AES cipher and encrypt/encode the text with it
    text = " ".join(text_split[1:])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encoded = encode_aes(cipher, text)

    # store the encoded text and IV in the DB for decoding later
    db.execute("insert or replace into encryption(encrypted, iv)"
               "values(:encoded,:iv)", {'encoded': encoded,
                                        'iv': iv_encoded})
    db.commit()

    return encoded.decode()


@asyncio.coroutine
@hook.command
def decrypt(text, bot, db, notice):
    """<pass> <string> - decrypts <string> with <pass>. (can only decrypt strings encrypted on this bot)
    :type bot: cloudbot.bot.CloudBot
    :type db: sqlalchemy.orm.session.Session
    """

    inp_split = text.split(" ")

    # if there is only one argument, return the help message
    if len(inp_split) == 1:
        notice(decrypt.__doc__)
        return

    encrypted_str = " ".join(inp_split[1:])

    # generate the key from the password and salt
    password = inp_split[0]
    salt = get_salt(bot)
    key = PBKDF2(password, salt).read(32)

    encrypted_bytes = encrypted_str.encode("utf-8")

    # get the encoded IV from the database
    database_result = db.execute("select iv from encryption where"
                                 " encrypted=:key", {'key': encrypted_bytes}).fetchone()

    if database_result is None:
        notice("Unknown encrypted string '{}'".format(encrypted_str))
        return

    # decode the IV
    iv_encoded = database_result[0]
    iv = base64.b64decode(iv_encoded)

    # create AES cipher, decode text, decrypt text, and unpad it
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return decode_aes(cipher, encrypted_bytes)
