from nums import median, clamp


def test_median_even_length():
    assert median([1, 2, 3, 4]) == 2.5


def test_median_odd_length_and_clamp():
    assert median([3, 1, 2]) == 2
    assert clamp(5, 0, 3) == 3
