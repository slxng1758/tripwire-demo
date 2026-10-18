from matrix import transpose, dot, identity


def test_transpose_rectangular():
    assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert transpose([[1], [2], [3]]) == [[1, 2, 3]]


def test_square_and_helpers():
    assert transpose([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]
    assert dot(identity(2), [[1, 2], [3, 4]]) == [[1, 2], [3, 4]]
