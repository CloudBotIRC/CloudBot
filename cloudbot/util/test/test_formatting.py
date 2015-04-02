from cloudbot.util.formatting import munge, dict_format, pluralize, strip_colors, truncate, truncate_str, \
    strip_html, multi_replace, multiword_replace, truncate_words, smart_split, get_text_list, ireplace, chunk_str

test_munge_input = "The quick brown fox jumps over the lazy dog"
test_munge_count = 3
test_munge_result_a = "Ţħë ʠüíċķ Бŗöωñ ƒöχ ĵüṁρš övëŗ ţħë ĺäźÿ đöġ"
test_munge_result_b = "Ţħë quick brown fox jumps over the lazy dog"

test_format_formats = ["{a} {b} {c}", "{a} {b}", "{a}"]
test_format_data = {"a": "First Thing", "b": "Second Thing"}
test_format_result = "First Thing Second Thing"

test_pluralize_num_a = 1
test_pluralize_num_b = 5
test_pluralize_result_a = "1 cake"
test_pluralize_result_b = "5 cakes"
test_pluralize_text = "cake"

test_strip_colors_input = "\x02I am bold\x02"
test_strip_colors_result = "I am bold"

test_truncate_str_input = "I am the example string for a unit test"
test_truncate_str_length_a = 10
test_truncate_str_length_b = 100
test_truncate_str_result_a = "I am the..."
test_truncate_str_result_b = "I am the example string for a unit test"

test_truncate_words_input = "I am the example string for a unit test"
test_truncate_words_length_a = 5
test_truncate_words_length_b = 100
test_truncate_words_result_a = "I am the example string..."
test_truncate_words_result_b = "I am the example string for a unit test"

test_strip_html_input = "<strong>Cats &amp; Dogs: &#181;</strong>"
test_strip_html_result = "Cats & Dogs: µ"

test_multiword_replace_dict = {"<bit1>": "<replace1>", "[bit2]": "[replace2]"}
test_multiword_replace_text = "<bit1> likes [bit2]"
test_multiword_replace_result = "<replace1> likes [replace2]"

test_ireplace_input = "The quick brown FOX fox FOX jumped over the lazy dog"

test_chunk_str_input = "The quick brown fox jumped over the lazy dog"
test_chunk_str_result = ['The quick', 'brown fox', 'jumped', 'over the', 'lazy dog']


def test_munge():
    assert munge(test_munge_input) == test_munge_result_a
    assert munge(test_munge_input, test_munge_count) == test_munge_result_b


def test_dict_format():
    assert dict_format(test_format_data, test_format_formats) == test_format_result
    assert dict_format({}, test_format_formats) is None


def test_pluralize():
    assert pluralize(test_pluralize_num_a, test_pluralize_text) == test_pluralize_result_a
    assert pluralize(test_pluralize_num_b, test_pluralize_text) == test_pluralize_result_b


def test_strip_colors():
    # compatibility
    assert strip_colors(test_strip_colors_input) == test_strip_colors_result


def test_truncate_str():
    assert truncate(test_truncate_str_input, length=test_truncate_str_length_a) == test_truncate_str_result_a
    assert truncate(test_truncate_str_input, length=test_truncate_str_length_b) == test_truncate_str_result_b

    # compatibility
    assert truncate_str(test_truncate_str_input, length=test_truncate_str_length_a) == test_truncate_str_result_a
    assert truncate_str(test_truncate_str_input, length=test_truncate_str_length_b) == test_truncate_str_result_b


# noinspection PyPep8
def test_truncate_words():
    assert truncate_words(test_truncate_words_input, length=test_truncate_words_length_a) == \
           test_truncate_words_result_a
    assert truncate_words(test_truncate_words_input, length=test_truncate_words_length_b) == \
           test_truncate_words_result_b


def test_strip_html():
    assert strip_html(test_strip_html_input) == test_strip_html_result


def test_multiword_replace():
    assert multi_replace(test_multiword_replace_text, test_multiword_replace_dict) == test_multiword_replace_result

    # compatibility
    assert multiword_replace(test_multiword_replace_text, test_multiword_replace_dict) == test_multiword_replace_result


def test_ireplace():
    assert ireplace(test_ireplace_input, "fox", "cat") == "The quick brown cat cat cat jumped over the lazy dog"
    assert ireplace(test_ireplace_input, "FOX", "cAt") == "The quick brown cAt cAt cAt jumped over the lazy dog"
    assert ireplace(test_ireplace_input, "fox", "cat", 1) == "The quick brown cat fox FOX jumped over the lazy dog"
    assert ireplace(test_ireplace_input, "fox", "cat", 2) == "The quick brown cat cat FOX jumped over the lazy dog"

    # test blank input - this should behave like the native string.replace()
    assert ireplace("Hello", "", "?") == "?H?e?l?l?o?"


def test_chunk_str():
    assert chunk_str(test_chunk_str_input, 10) == test_chunk_str_result


def test_get_text_list():
    assert get_text_list(['a', 'b', 'c', 'd']) == 'a, b, c or d'
    assert get_text_list(['a', 'b', 'c'], 'and') == 'a, b and c'
    assert get_text_list(['a', 'b'], 'and') == 'a and b'
    assert get_text_list(['a']) == 'a'
    assert get_text_list([]) == ''


def test_smart_split():
    assert list(smart_split(r'This is "a person\'s" test.')) == ['This', 'is', '"a person\\\'s"', 'test.']
    assert list(smart_split(r"Another 'person\'s' test.")) == ['Another', "'person\\'s'", 'test.']
    assert list(smart_split(r'A "\"funky\" style" test.')) == ['A', '"\\"funky\\" style"', 'test.']
