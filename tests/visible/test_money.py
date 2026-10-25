"""Visible tests for ledgerly.money — develop against these."""

from decimal import Decimal

from ledgerly.money import from_cents, sum_cents, to_cents


def test_to_cents_converts_exact_dollar_string():
    assert to_cents("19.99") == 1999


def test_to_cents_handles_whole_dollar_amount():
    assert to_cents("5.00") == 500


def test_to_cents_accepts_decimal_input():
    assert to_cents(Decimal("19.99")) == 1999


def test_to_cents_rejects_float():
    import pytest

    with pytest.raises(TypeError):
        to_cents(19.99)  # type: ignore[arg-type]


def test_from_cents_formats_two_decimal_places():
    assert from_cents(1999) == "19.99"
    assert from_cents(500) == "5.00"


def test_sum_cents_adds_exactly_across_many_amounts():
    # The classic float trap: 0.1 + 0.2 != 0.3 in binary floating point.
    assert sum_cents(["0.10", "0.20"]) == 30


def test_sum_cents_reconciles_a_long_sequence_exactly():
    amounts = ["19.99"] * 100
    assert sum_cents(amounts) == 1999 * 100
