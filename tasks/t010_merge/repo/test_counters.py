from counters import merge_counts, total


def test_merge_adds_shared_keys():
    assert merge_counts({"a": 1, "b": 2}, {"b": 5, "c": 1}) == {"a": 1, "b": 7, "c": 1}


def test_inputs_not_mutated_and_total_works():
    a = {"x": 1}
    merge_counts(a, {"x": 2})
    assert a == {"x": 1}
    assert total({"x": 2, "y": 3}) == 5
