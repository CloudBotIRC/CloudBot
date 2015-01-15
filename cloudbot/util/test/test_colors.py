import pytest

from cloudbot.util.colors import parse, strip, get_available_colours, get_available_formats, get_color, get_format, \
    _convert, strip_irc, strip_all, IRC_COLOUR_DICT

test_input = "The quick $(brown, red)brown$(clear) fox$(fake) jumps over the $(bold)lazy dog$(clear)."

test_parse_output = "The quick \x0305,04brown\x0f fox jumps over the \x02lazy dog\x0f."
test_strip_output = "The quick brown fox jumps over the lazy dog."

test_strip_irc_input = "\x02I am $(bold)bold\x02"
test_strip_irc_result = "I am $(bold)bold"
test_strip_all_result = "I am bold"


def test_parse():
    assert parse(test_input) == test_parse_output


def test_strip():
    assert strip(test_input) == test_strip_output
    assert strip_irc(test_strip_irc_input) == test_strip_irc_result
    assert strip_all(test_strip_irc_input) == test_strip_all_result


def test_available_colors():
    assert "dark_grey" in get_available_colours()


def test_available_formats():
    assert "bold" in get_available_formats()


def test_invalid_color():
    with pytest.raises(KeyError) as excinfo:
        get_color("cake")
    assert 'not in the list of available colours' in str(excinfo.value)


def test_invalid_format():
    with pytest.raises(KeyError) as excinfo:
        get_format("cake")
    assert 'not found in the list of available formats' in str(excinfo.value)


def test_get_color():
    assert get_color("red") == "\x0304"
    assert get_color("red", return_formatted=False) == "04"


def test_get_random_color():
    assert get_color("random") in ["\x03" + i for i in IRC_COLOUR_DICT.values()]
    assert get_color("random", return_formatted=False) in list(IRC_COLOUR_DICT.values())


def test_get_format():
    assert get_format("bold") == "\x02"


def test_convert():
    assert _convert("$(red, green)") == "\x0304,09"
    assert _convert("$(red, bold)") == "\x0304\x02"
    assert _convert("$(red)") == "\x0304"
    assert _convert("$(bold)") == "\x02"
    assert _convert("cats") == "cats"
