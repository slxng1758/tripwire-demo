"""A minimal in-memory log buffer used by the CLI tools."""

LEVELS = ("debug", "info", "warn", "error")


def level_rank(level):
    """Numeric rank of a level name (debug=0 ... error=3)."""
    return LEVELS.index(level)


def format_entry(level, message):
    """Render one entry as '[LEVEL] message'."""
    return f"[{level.upper()}] {message}"


def at_least(entries, level):
    """Entries (level, message) at or above the given level."""
    return [e for e in entries if level_rank(e[0]) >= level_rank(level)]


def render(entries):
    """All entries rendered, one per line."""
    return "\n".join(format_entry(l, m) for l, m in entries)


def record(level, message, buffer=[]):
    """Append an entry to `buffer` and return the buffer. A new empty buffer is used when none is given."""
    buffer.append((level, message))
    return buffer
