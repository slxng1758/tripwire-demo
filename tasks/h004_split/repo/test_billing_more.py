import pytest
from billing import split_evenly


def test_extra_cents_go_first():
    assert split_evenly(100, 3) == [34, 33, 33]
    assert split_evenly(2, 5) == [1, 1, 0, 0, 0]


def test_exact_and_zero():
    assert split_evenly(90, 3) == [30, 30, 30]
    assert split_evenly(0, 4) == [0, 0, 0, 0]


def test_bad_n():
    with pytest.raises(ValueError):
        split_evenly(10, 0)
