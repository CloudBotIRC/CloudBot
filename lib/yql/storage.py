import os
from hashlib import md5

from yql import YahooToken

SECRET = "FDHSJLUREIRPpieruweruwoeirhfsdjf"


class TokenStoreError(Exception):
    """Generic token storage"""
    pass


class BaseTokenStore(object):
    """Base class for storage"""

    def set(self, name, token):
        raise NotImplementedError

    def get(self, name):
        raise NotImplementedError


class FileTokenStore(BaseTokenStore):
    """A simple filesystem based token store

    Note: this is more intended as an example rather than
    something for heavy duty production usage.

    """

    def __init__(self, dir_path, secret=None):
        """Initialize token storage"""

        if not os.path.exists(dir_path):
            raise TokenStoreError("Path is not valid")

        self.base_dir = dir_path
        self.secret = secret or SECRET

    def get_filepath(self, name):
        """Build filepath"""

        filename = md5("%s%s" % (name, self.secret)).hexdigest()
        filepath = os.path.join(self.base_dir, filename)

        return filepath

    def set(self, name, token):
        """Write a token to file"""

        if hasattr(token, 'key'):
            token = YahooToken.to_string(token)

        if token:
            filepath = self.get_filepath(name)
            f_handle = open(filepath, 'w')
            f_handle.write(token)
            f_handle.close()

    def get(self, name):
        """Get a token from the filesystem"""

        filepath = self.get_filepath(name)

        if os.path.exists(filepath):
            f_handle = open(filepath, 'r')
            token = f_handle.read()
            f_handle.close()

            token = YahooToken.from_string(token)
            return token
