"""Tiny matrix helpers. Matrices are lists of equal-length row lists."""


def shape(m):
    """(rows, cols)."""
    return (len(m), len(m[0]) if m else 0)


def identity(n):
    """n x n identity matrix."""
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def add(a, b):
    """Element-wise sum of equal-shaped matrices."""
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def scale(m, k):
    """Multiply every element by k."""
    return [[x * k for x in row] for row in m]


def row_sums(m):
    """Sum of each row."""
    return [sum(row) for row in m]


def column(m, j):
    """Column j as a list."""
    return [row[j] for row in m]


def dot(a, b):
    """Matrix product a x b."""
    cols = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, c)) for c in cols] for row in a]


def transpose(m):
    """Rows become columns."""
    n = len(m)
    return [[m[i][j] for i in range(n)] for j in range(n)]
