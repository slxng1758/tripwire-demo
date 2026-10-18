"""Text fitting helpers for fixed-width displays."""


def pad_right(s, width):
    """Pad with spaces to the given width (never cuts)."""
    return s + " " * max(width - len(s), 0)


def center(s, width):
    """Center s in `width` columns, extra space on the right."""
    left = max(width - len(s), 0) // 2
    return " " * left + s + " " * max(width - len(s) - left, 0)


def fits(s, width):
    """True if s fits in width columns."""
    return len(s) <= width


def shorten(s, width):
    """Shorten s to fit in `width` characters, marking the cut with an ellipsis."""
    if len(s) <= width:
        return s
    return s[:width] + "..."
