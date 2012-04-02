import hashlib
from util import hook


@hook.command
def md5(inp):
    ".hash <text> -- Returns a md5 hash of <text>."
    return hashlib.md5(inp).hexdigest()


@hook.command
def sha1(inp):
    ".hash <text> -- Returns a sha1 hash of <text>."
    return hashlib.sha1(inp).hexdigest()


@hook.command
def sha256(inp):
    ".hash <text> -- Returns a sha256 hash of <text>."
    return hashlib.sha256(inp).hexdigest()


@hook.command
def sha512(inp):
    ".hash <text> -- Returns a sha512 hash of <text>."
    return hashlib.sha512(inp).hexdigest()


@hook.command
def hash(inp):
    ".hash <text> -- Returns hashes of <text>."
    return ', '.join(x + ": " + getattr(hashlib, x)(inp).hexdigest()
            for x in 'md5 sha1 sha256'.split())
