from textfit import shorten, pad_right


def test_shorten_basic():
    assert shorten("hello world", 8) == "hello..."
    assert shorten("hi", 8) == "hi"


def test_pad_still_works():
    assert pad_right("ab", 4) == "ab  "
