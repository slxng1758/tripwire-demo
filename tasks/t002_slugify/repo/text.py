"""Text helpers for building URLs and file names.

All functions are pure and take and return strings.
"""


def strip_accents(s):
    """Remove a few common accented characters."""
    table = {"é": "e", "è": "e", "à": "a", "ü": "u", "ö": "o", "ñ": "n"}
    return "".join(table.get(c, c) for c in s)


def collapse_spaces(s):
    """Collapse runs of whitespace into single spaces."""
    return " ".join(s.split())


def truncate(s, n):
    """Cut a string to at most n characters."""
    return s[:n]


def title_case(s):
    """Capitalise each word."""
    return " ".join(w.capitalize() for w in s.split())


def slugify(s):
    """Lowercase, hyphen-separated slug with accents removed."""
    s = strip_accents(collapse_spaces(s))
    return s.replace(" ", "_")
