from versions import compare, major


def test_numeric_components():
    assert compare("1.10", "1.9") == 1
    assert compare("1.2", "1.10") == -1


def test_major_still_works():
    assert major("3.4") == 3
