import time

from cloudbot.util.tokenbucket import TokenBucket


# noinspection PyProtectedMember
def test_bucket_consume():
    bucket = TokenBucket(10, 5)
    # larger then capacity
    assert bucket.consume(15) is False
    # success
    assert bucket.consume(10) is True
    # check if bucket has no tokens
    assert bucket._tokens == 0
    # bucket is empty from above, should fail
    assert bucket.consume(10) is False


# noinspection PyProtectedMember
def test_bucket_advanced():
    bucket = TokenBucket(10, 1)
    # tokens start at 10
    assert bucket._tokens == 10
    # empty tokens
    assert bucket.empty() is True
    # check tokens is 0
    assert bucket._tokens == 0
    # refill tokens
    assert bucket.refill() is True
    # check tokens is 10
    assert bucket._tokens == 10


def test_bucket_regen():
    bucket = TokenBucket(10, 10)
    # success
    assert bucket.consume(10) is True
    # sleep
    time.sleep(1)
    # bucket should be full again and this should succeed
    assert bucket.tokens == 10
    assert bucket.consume(10) is True
