"""Product catalog for the demo shop."""

PRICES = {"pen": 1.50, "notebook": 4.00, "bag": 25.00, "lamp": 18.75}


def price_of(item):
    """Unit price of an item."""
    return PRICES[item]


def known(item):
    """True if the catalog has the item."""
    return item in PRICES
