"""Small finance helpers for the savings calculator."""


def percent(part, whole):
    """part as a percentage of whole (0.0 if whole is zero)."""
    return 100.0 * part / whole if whole else 0.0


def simple_interest(principal, rate, years):
    """Interest earned with no compounding. rate is a fraction (0.05 = 5%)."""
    return principal * rate * years


def monthly_payment(principal, annual_rate, months):
    """Level monthly payment for a loan (zero-interest loans split evenly)."""
    if annual_rate == 0:
        return principal / months
    r = annual_rate / 12
    return principal * r / (1 - (1 + r) ** -months)


def rule_of_72(rate_percent):
    """Approximate years to double at the given percent rate."""
    return 72 / rate_percent


def future_value_annuity(payment, rate, periods):
    """Future value of equal payments made at the end of each period."""
    return payment * (((1 + rate) ** periods - 1) / rate)


def compound_balance(principal, rate, years):
    """Balance after compounding once per year. rate is a fraction."""
    return principal * (1 + rate * years)
