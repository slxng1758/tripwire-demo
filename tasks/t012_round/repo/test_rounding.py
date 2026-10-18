from rounding import round_half_up, ceil_div, clamp


def test_halves_go_up():
    assert round_half_up(2.5) == 3
    assert round_half_up(0.5) == 1
    assert round_half_up(3.5) == 4
    assert round_half_up(2.4) == 2


def test_helpers_still_work():
    assert ceil_div(7, 2) == 4
    assert clamp(9, 0, 5) == 5
