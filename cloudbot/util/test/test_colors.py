from cloudbot.util.colors import parse, strip, get_available_colours, get_available_formats

test_input = "The quick $(brown)brown$(clear) fox jumps over the$(bold) lazy dog$(clear)."

test_parse_output = "The quick \x0305brown\x0f fox jumps over the\x02 lazy dog\x0f."
test_strip_output = "The quick brown fox jumps over the lazy dog."


def test_parse():
    assert parse(test_input) == test_parse_output


def test_strip():
    assert strip(test_input) == test_strip_output


def test_available_colors():
    assert "dark_grey" in get_available_colours()


def test_available_formats():
    assert "bold" in get_available_formats()