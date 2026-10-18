from versions import compare, newest


def test_trailing_zeros_equal():
    assert compare("1.0", "1.0.0") == 0
    assert compare("2", "2.0.0") == 0
    assert compare("1.0.1", "1.0") == 1


def test_newest():
    assert newest(["1.9", "1.10", "1.2.5"]) == "1.10"
    assert newest(["1.0", "1.0.0"]) in ("1.0", "1.0.0")
