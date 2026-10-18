"""Dotted version helpers. Versions are strings such as '2.0' or '1.10.3'."""


def parse(v):
    """'1.10.3' -> [1, 10, 3]."""
    return [int(x) for x in v.split(".")]


def major(v):
    """Major component as an int."""
    return parse(v)[0]


def is_prerelease(v):
    """True for versions below 1.0."""
    return major(v) < 1


def newest(versions):
    """The newest of a non-empty list of version strings."""
    best = versions[0]
    for v in versions[1:]:
        if compare(v, best) > 0:
            best = v
    return best


def compare(a, b):
    """-1 if version a is older than b, 0 if the same, 1 if newer."""
    return (a > b) - (a < b)
