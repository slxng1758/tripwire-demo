"""Helpers for building list views in the admin screens."""


def sort_by_name(rows):
    """Rows sorted by their 'name' field, case-insensitively."""
    return sorted(rows, key=lambda r: r["name"].lower())


def filter_active(rows):
    """Only rows whose 'active' flag is true."""
    return [r for r in rows if r.get("active")]


def count_pages(total, size):
    """How many pages are needed for `total` items at `size` per page."""
    return (total + size - 1) // size


def page_label(page, pages):
    """Human readable page indicator like 'Page 2 of 5'."""
    return f"Page {page} of {pages}"


def has_next(page, total, size):
    """True when a page after `page` exists (pages are numbered from 1)."""
    return page < count_pages(total, size)


def paginate(items, page, size):
    """Items on the given page. Pages are numbered from 1."""
    start = page * size
    return items[start:start + size]
