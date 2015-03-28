from cloudbot.util.filesize import size, si, verbose
import cloudbot.util.filesize as fs


def test_size():
    # Using the traditional system, where a factor of 1024 is used
    assert size(10) == "10B"
    assert size(100) == "100B"
    assert size(1000) == "1000B"
    assert size(2000) == "1K"
    assert size(10000) == "9K"
    assert size(20000) == "19K"
    assert size(100000) == "97K"
    assert size(200000) == "195K"
    assert size(1000000) == "976K"
    assert size(2000000) == "1M"


def test_size_verbose():
    # Using the verbose system, where a factor of 1024 is used
    assert size(1, system=verbose) == "1 byte"
    assert size(1000, system=verbose) == "1000 bytes"
    assert size(2000, system=verbose) == "1 kilobyte"
    assert size(10000, system=verbose) == "9 kilobytes"
    assert size(2000000, system=verbose) == "1 megabyte"
    assert size(30000000, system=verbose) == "28 megabytes"


def test_size_si():
    # Using the SI system, with a factor of 1000
    assert size(10, system=si) == "10B"
    assert size(100, system=si) == "100B"
    assert size(1000, system=si) == "1K"
    assert size(2000, system=si) == "2K"
    assert size(10000, system=si) == "10K"
    assert size(20000, system=si) == "20K"
    assert size(100000, system=si) == "100K"
    assert size(200000, system=si) == "200K"
    assert size(1000000, system=si) == "1M"
    assert size(2000000, system=si) == "2M"


def test_size_alias():
    assert size(1, system=fs.V) == "1 byte"

