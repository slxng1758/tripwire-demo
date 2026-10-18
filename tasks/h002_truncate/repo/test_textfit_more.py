from textfit import shorten


def test_shorten_exact_and_small():
    assert shorten("abcdef", 6) == "abcdef"
    assert shorten("abcdefg", 6) == "abc..."
    assert shorten("abcdefg", 3) == "..."
    assert shorten("abcdefg", 2) == ".."
    assert shorten("abcdefg", 0) == ""
