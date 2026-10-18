"""Small collection helpers."""


def chunk(items, size):
    """Split a list into lists of at most `size` items."""
    return [items[i:i + size] for i in range(0, len(items), size)]


def flatten(nested):
    """One level of flattening."""
    return [x for sub in nested for x in sub]


def first(items, default=None):
    """First item or default."""
    return items[0] if items else default


def last(items, default=None):
    """Last item or default."""
    return items[-1] if items else default


def pairwise(items):
    """Consecutive pairs."""
    return list(zip(items, items[1:]))


def partition(items, pred):
    """(matching, non_matching) lists."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return yes, no


def unique(items):
    """Items with duplicates removed, keeping the first occurrence in original order."""
    return list(set(items))
