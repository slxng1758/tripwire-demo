from leaderboard import top_n, rank_of


def test_top_n():
    s = [("a", 5), ("b", 9), ("c", 7), ("d", 1)]
    assert top_n(s, 2) == [("b", 9), ("c", 7)]


def test_rank_still_works():
    assert rank_of([("a", 5), ("b", 9)], "a") == 2
