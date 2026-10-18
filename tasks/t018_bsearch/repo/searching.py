"""Searching helpers over sorted lists."""


def linear_search(items, target):
    """Index of target by scanning, or -1."""
    for i, x in enumerate(items):
        if x == target:
            return i
    return -1


def is_sorted(items):
    """True if items are in non-decreasing order."""
    return all(a <= b for a, b in zip(items, items[1:]))


def count_in_range(items, lo, hi):
    """How many sorted items fall in [lo, hi]."""
    return sum(1 for x in items if lo <= x <= hi)


def lower_bound(items, target):
    """Index of the first element >= target in a sorted list."""
    lo, hi = 0, len(items)
    while lo < hi:
        mid = (lo + hi) // 2
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def insert_sorted(items, value):
    """New list with value inserted keeping order."""
    i = lower_bound(items, value)
    return items[:i] + [value] + items[i:]


def binary_search(items, target):
    """Index of target in a sorted list, or -1 if absent."""
    lo, hi = 0, len(items) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
