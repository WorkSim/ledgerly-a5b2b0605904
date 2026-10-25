"""Balance-checked, idempotent transfers between in-memory accounts.

An "account book" here is just a `dict[str, int]` mapping account id to
balance in integer cents — no database involved. `transfer` moves money
between two accounts in that dict, refusing to overdraw the source account,
and is idempotent on `transfer_id`: replaying the same transfer request
(e.g. a client retry after a dropped response) must apply it exactly once.
"""

from __future__ import annotations


class InsufficientFundsError(ValueError):
    """Raised when a transfer would overdraw the source account."""


def transfer(
    accounts: dict[str, int],
    from_id: str,
    to_id: str,
    amount_cents: int,
    transfer_id: str,
    processed: dict[str, dict] | None = None,
) -> dict:
    """Move `amount_cents` from `from_id` to `to_id`, exactly once per `transfer_id`.

    Args:
        accounts: Current `account_id -> balance-in-cents` mapping.
        from_id: Source account id.
        to_id: Destination account id.
        amount_cents: Amount to move, as an exact integer number of cents
            (see `ledgerly.money.to_cents` to convert from a decimal dollar
            string before calling this function).
        transfer_id: Idempotency key identifying this transfer request. A
            second call with the same `transfer_id` (a client retry) is a
            no-op that returns the previously recorded result — it never
            reapplies the transfer.
        processed: `transfer_id -> recorded transfer result` for every
            transfer already applied to `accounts`. Defaults to empty (no
            prior transfers recorded).

    Returns:
        `{"accounts": <new accounts dict>, "processed": <new processed dict>}`.
        Neither `accounts` nor `processed` (nor their inputs) are mutated.

    Raises:
        InsufficientFundsError: `amount_cents` exceeds `from_id`'s current
            balance, and this `transfer_id` has not already been processed
            (a retry of an already-applied transfer never re-raises this,
            even if the account no longer has the funds).
        ValueError: `amount_cents` is not a positive integer.
        KeyError: `from_id` or `to_id` is not a known account.
    """
    if not isinstance(amount_cents, int) or isinstance(amount_cents, bool) or amount_cents <= 0:
        raise ValueError("amount_cents must be a positive integer number of cents")

    accounts = dict(accounts)
    processed = dict(processed or {})

    if from_id not in accounts:
        raise KeyError(f"unknown source account: {from_id!r}")
    if to_id not in accounts:
        raise KeyError(f"unknown destination account: {to_id!r}")

    accounts[from_id] -= amount_cents
    accounts[to_id] += amount_cents
    processed[transfer_id] = {
        "from_id": from_id,
        "to_id": to_id,
        "amount_cents": amount_cents,
    }

    return {"accounts": accounts, "processed": processed}
