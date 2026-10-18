from shop.pricing import discounted_total, line_total


def test_bulk_discount_threshold():
    assert discounted_total([("pen", 10)]) == 12.75
    assert discounted_total([("pen", 9)]) == 13.5
    assert discounted_total([("pen", 12), ("bag", 1)]) == 40.3


def test_line_total_still_works():
    assert line_total("notebook", 3) == 12.0
