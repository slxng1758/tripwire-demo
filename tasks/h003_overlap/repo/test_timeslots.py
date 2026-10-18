from timeslots import overlaps, duration


def test_partial_overlap():
    assert overlaps((1, 5), (4, 8))
    assert not overlaps((1, 3), (6, 9))


def test_duration_still_works():
    assert duration((2, 7)) == 5
