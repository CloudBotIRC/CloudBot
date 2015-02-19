"""
tokenbucket.py

A python implementation of the token bucket algorithm.
Adapted from <http://code.activestate.com/recipes/511490-implementation-of-the-token-bucket-algorithm/>

Maintainer:
    - Luke Rogers <https://github.com/lukeroge>

License:
    Python Software Foundation License (PSF)
"""

from time import time


class TokenBucket(object):
    """An implementation of the token bucket algorithm.
    >> bucket = TokenBucket(80, 0.5)
    >> bucket.consume(10)
    True
    >> bucket.consume(90)
    False
    """

    def __init__(self, _capacity, fill_rate):
        """
        :param _capacity: The total amount of token the bucket can contain
        :param fill_rate: The rate at which tokens regenerate. (fill_rate per second)
        """
        """tokens is the total tokens in the bucket. fill_rate is the
        rate in tokens/second that the bucket will be refilled."""
        self.capacity = float(_capacity)
        self._tokens = float(_capacity)
        self.fill_rate = float(fill_rate)
        self.timestamp = time()

    def consume(self, tokens):
        """
        Consume tokens from the bucket.
        :param tokens: The number of tokens to consume
        :return true if there were sufficient tokens otherwise false
        """
        if tokens <= self.tokens:
            self._tokens -= tokens
        else:
            return False
        return True

    def refill(self):
        """
        Sets the current token count to the max capacity
        """
        self._tokens = self.capacity
        return True

    def empty(self):
        """
        Sets the current token count to zero
        """
        self._tokens = float(0)
        return True

    def get_tokens(self):
        """
        Calculates and returns the current amount of tokens the bucker contains

        :return Amount of tokens the bucket contains
        :rtype Float
        """
        now = time()
        if self._tokens < self.capacity:
            delta = self.fill_rate * (now - self.timestamp)
            self._tokens = min(self.capacity, self._tokens + delta)
        self.timestamp = now
        return self._tokens

    tokens = property(get_tokens)
