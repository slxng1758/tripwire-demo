from timeslots import overlaps


def test_order_does_not_matter():
    assert overlaps((4, 8), (1, 5))


def test_touching_does_not_overlap():
    assert not overlaps((1, 5), (5, 8))
    assert not overlaps((5, 8), (1, 5))


def test_containment_and_equal():
    assert overlaps((1, 9), (2, 3))
    assert overlaps((2, 3), (1, 9))
    assert overlaps((1, 5), (1, 5))
    assert overlaps((1, 5), (1, 3))
