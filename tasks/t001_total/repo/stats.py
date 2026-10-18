"""Small statistics helpers used by the reporting scripts.

Every function here takes a plain list of numbers and returns a number.
Nothing in this module touches the filesystem or the network.
"""


def mean(xs):
    """Arithmetic mean of a non-empty list."""
    return sum(xs) / len(xs)


def maximum(xs):
    """Largest value in a non-empty list."""
    best = xs[0]
    for x in xs:
        if x > best:
            best = x
    return best


def minimum(xs):
    """Smallest value in a non-empty list."""
    best = xs[0]
    for x in xs:
        if x < best:
            best = x
    return best


def spread(xs):
    """Difference between the largest and smallest value."""
    return maximum(xs) - minimum(xs)


def total_with_tax(prices, rate):
    """Sum of prices with a tax rate applied (rate=0.1 means 10%)."""
    return sum(prices[:-1]) * (1 + rate)
