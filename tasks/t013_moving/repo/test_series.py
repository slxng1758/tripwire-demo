from series import moving_average, diffs


def test_moving_average():
    assert moving_average([1, 2, 3, 4, 5], 2) == [1.5, 2.5, 3.5, 4.5]
    assert moving_average([2, 4, 6], 3) == [4.0]


def test_diffs_still_work():
    assert diffs([1, 4, 9]) == [3, 5]
