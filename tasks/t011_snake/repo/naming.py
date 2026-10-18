"""Identifier naming helpers for the code generator."""


def is_snake(name):
    """True if name is lower-case words joined by single underscores."""
    return name == name.lower() and "__" not in name and not name.startswith("_")


def snake_to_camel(name):
    """userName from user_name."""
    first, *rest = name.split("_")
    return first + "".join(w.capitalize() for w in rest)


def snake_to_pascal(name):
    """UserName from user_name."""
    return "".join(w.capitalize() for w in name.split("_"))


def pluralize(name):
    """Very small English plural helper."""
    if name.endswith("y"):
        return name[:-1] + "ies"
    return name + "s"


def strip_prefix(name, prefix):
    """Remove prefix if present."""
    return name[len(prefix):] if name.startswith(prefix) else name


def camel_to_snake(name):
    """user_name from userName or UserName."""
    out = []
    for ch in name:
        if ch.isupper():
            out.append("_" + ch.lower())
        else:
            out.append(ch)
    return "".join(out)
