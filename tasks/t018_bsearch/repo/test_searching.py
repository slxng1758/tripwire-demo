from searching import binary_search, lower_bound


def test_binary_search_finds_every_element():
    items = [1, 3, 5, 7, 9, 11]
    for i, x in enumerate(items):
        assert binary_search(items, x) == i
    assert binary_search(items, 4) == -1
    assert binary_search([], 1) == -1


def test_lower_bound_still_works():
    assert lower_bound([1, 3, 5], 4) == 2
