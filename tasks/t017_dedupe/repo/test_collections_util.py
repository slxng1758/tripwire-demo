from collections_util import unique, chunk


def test_unique_keeps_first_occurrence_order():
    assert unique([3, 1, 3, 2, 1, 9]) == [3, 1, 2, 9]
    assert unique(["b", "a", "b"]) == ["b", "a"]


def test_chunk_still_works():
    assert chunk([1, 2, 3], 2) == [[1, 2], [3]]
