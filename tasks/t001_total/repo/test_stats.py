from stats import total_with_tax, mean, spread


def test_total_with_tax():
    assert abs(total_with_tax([10, 20, 30], 0.1) - 66.0) < 1e-9


def test_mean_and_spread_still_work():
    assert mean([1, 2, 3]) == 2
    assert spread([1, 5, 3]) == 4
