"""Parse key=value configuration text."""


def clean_lines(text):
    """Non-empty, non-comment lines with surrounding whitespace removed."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def split_pair(line):
    """Split 'key=value' into (key, value), trimming spaces. The value may itself contain '='."""
    key, value = line.split("=")[:2]
    return key.strip(), value.strip()


def parse(text):
    """Parse configuration text into a dict."""
    return dict(split_pair(l) for l in clean_lines(text))
