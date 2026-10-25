"""Grading suite for LEDG-208 — currency amounts are exact to the cent.

Acceptance criteria:
  - Amounts are exact to the cent for all supported operations (no
    float-rounding drift on conversion).
  - A sequence of transfers reconciles exactly to the expected total
    balance, however many amounts are combined.
"""

from decimal import Decimal

from ledgerly.ledger import transfer
from ledgerly.money import from_cents, sum_cents, to_cents


def test_to_cents_is_exact_for_amount_that_floats_mis_truncate():
    # float(19.99) * 100 == 1998.9999999999998 -> naive int() truncation
    # loses a cent here. Decimal-based conversion must not.
    assert to_cents("19.99") == 1999


def test_to_cents_is_exact_for_repeating_binary_fraction_amount():
    # 0.1 has no exact binary float representation; float-based conversion
    # is prone to drifting off the exact cent value.
    assert to_cents("0.10") == 10
    assert to_cents("0.20") == 20
    assert to_cents("0.30") == 30


def test_from_cents_round_trips_to_cents_exactly():
    for dollars in ["0.01", "0.10", "1.00", "19.99", "1234.56"]:
        assert from_cents(to_cents(dollars)) == dollars


def test_sum_of_many_small_amounts_reconciles_exactly():
    # A classic float trap: summing 0.1 ten times in float drifts away
    # from 1.00 by a tiny epsilon. The cents total must be exact.
    assert sum_cents(["0.10"] * 10) == 100


def test_sum_cents_matches_decimal_ground_truth():
    amounts = ["19.99", "0.10", "0.20", "5.00", "1234.56"]
    expected = int(sum(Decimal(a) for a in amounts) * 100)

    assert sum_cents(amounts) == expected


def test_long_sequence_of_transfers_reconciles_to_expected_total():
    accounts = {"alice": to_cents("1000.00"), "bob": 0}
    amount = to_cents("19.99")

    for i in range(50):
        result = transfer(accounts, "alice", "bob", amount, transfer_id=f"t{i}")
        accounts = result["accounts"]

    expected_bob = amount * 50
    expected_alice = to_cents("1000.00") - expected_bob
    assert accounts == {"alice": expected_alice, "bob": expected_bob}
    assert accounts["alice"] + accounts["bob"] == to_cents("1000.00")
