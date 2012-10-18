import hashlib
from util import hook


@hook.command
def hash(inp):
    "hash <text> -- Returns hashes of <text>."
    return ', '.join(x + ": " + getattr(hashlib, x)(inp).hexdigest()
            for x in ['md5', 'sha1', 'sha256'])
