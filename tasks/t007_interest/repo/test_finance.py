from finance import compound_balance, simple_interest


def test_compound_balance():
    assert abs(compound_balance(1000, 0.05, 2) - 1102.5) < 1e-9
    assert abs(compound_balance(200, 0.1, 3) - 266.2) < 1e-9


def test_simple_interest_still_works():
    assert simple_interest(1000, 0.05, 2) == 100.0
