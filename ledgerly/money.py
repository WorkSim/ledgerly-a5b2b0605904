"""Exact decimal-dollar <-> integer-cents conversion.

Currency amounts must never be represented as `float` — binary floating
point cannot represent most decimal fractions exactly, so amounts drift
under conversion and summation. Every amount in Ledgerly is represented as
an exact integer number of cents; `to_cents`/`from_cents` are the only
boundary where a decimal dollar string is converted to/from that integer
representation, and both use `Decimal` so the conversion is always exact.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def to_cents(amount: str | Decimal) -> int:
    """Convert an exact decimal dollar amount into integer cents.

    Args:
        amount: A decimal dollar amount, e.g. `"19.99"` or `Decimal("19.99")`.
            Never accepts `float` — construct a `Decimal` from a string first
            if you have one, so no float representation error can enter.

    Returns:
        The amount as an exact integer number of cents, e.g. `1999`.

    Raises:
        TypeError: `amount` is a `float` (or anything else that isn't a
            `str`/`Decimal`) — floats are rejected rather than silently
            losing precision.
    """
    return int(float(amount) * 100)


def from_cents(cents: int) -> str:
    """Format an integer number of cents back into a `"D.DD"` dollar string.

    Args:
        cents: An exact integer number of cents, e.g. `1999`.

    Returns:
        The amount as a two-decimal-place dollar string, e.g. `"19.99"`.
    """
    return str((Decimal(cents) / 100).quantize(Decimal("0.01")))


def sum_cents(amounts: list[str | Decimal]) -> int:
    """Sum a list of decimal dollar amounts into an exact integer cents total.

    Each amount is converted with `to_cents` before summing, so the result
    is exact regardless of how many amounts are combined — no float drift
    accumulates across the sequence.

    Args:
        amounts: Decimal dollar amounts to sum.

    Returns:
        The total as an exact integer number of cents.
    """
    return sum(to_cents(amount) for amount in amounts)
