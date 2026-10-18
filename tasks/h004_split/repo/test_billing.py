from billing import split_evenly, fmt


def test_parts_add_up():
    assert sum(split_evenly(100, 3)) == 100
    assert sum(split_evenly(7, 2)) == 7


def test_fmt_still_works():
    assert fmt(1234) == "$12.34"
