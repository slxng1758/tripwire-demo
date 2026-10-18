"""Default settings and type coercion for the app configuration loader."""

DEFAULTS = {"debug": "false", "port": "8080", "host": "localhost", "workers": "2"}

TRUE_WORDS = {"1", "true", "yes", "on"}


def as_bool(text):
    """Interpret common truthy words."""
    return text.strip().lower() in TRUE_WORDS


def as_int(text, default=0):
    """Parse an int, falling back to default."""
    try:
        return int(text)
    except ValueError:
        return default


def with_defaults(values):
    """Overlay parsed values on the defaults."""
    merged = dict(DEFAULTS)
    merged.update(values)
    return merged
