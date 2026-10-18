"""Order pricing rules.

Bulk rule: orders of 10 or more units of a single line get 15% off that line.
"""

from shop.catalog import price_of

BULK_MIN = 10
BULK_RATE = 0.15


def line_total(item, qty):
    """Price of one order line before discounts."""
    return price_of(item) * qty


def apply_bulk(amount, qty):
    """Apply the bulk discount to a line amount when the quantity qualifies."""
    if qty > BULK_MIN:
        return amount * (1 - BULK_RATE)
    return amount


def discounted_total(order):
    """Total for an order given as a list of (item, qty) pairs."""
    return round(sum(apply_bulk(line_total(i, q), q) for i, q in order), 2)
