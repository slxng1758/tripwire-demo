from rankstats import percentile, mean


def test_percentile_max():
    assert percentile([1, 2, 3, 4, 5], 100) == 5
    assert percentile([5, 1, 3], 100) == 5


def test_mean_still_works():
    assert mean([1, 2, 3]) == 2
