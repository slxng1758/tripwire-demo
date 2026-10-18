from rankstats import percentile


def test_percentile_nearest_rank():
    data = [15, 20, 35, 40, 50]
    assert percentile(data, 5) == 15
    assert percentile(data, 20) == 15
    assert percentile(data, 30) == 20
    assert percentile(data, 40) == 20
    assert percentile(data, 50) == 35


def test_percentile_zero_and_empty():
    assert percentile([4, 2, 9], 0) == 2
    assert percentile([], 50) is None
    assert percentile([7], 100) == 7
