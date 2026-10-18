from listing import paginate, count_pages, has_next


def test_first_and_later_pages():
    items = list(range(1, 11))
    assert paginate(items, 1, 4) == [1, 2, 3, 4]
    assert paginate(items, 3, 4) == [9, 10]


def test_helpers_still_work():
    assert count_pages(10, 4) == 3
    assert has_next(1, 10, 4)
