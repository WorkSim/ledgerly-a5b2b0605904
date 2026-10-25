"""Grading suite for LEDG-215 — retried transfers apply exactly once.

Acceptance criteria:
  - Submitting the same transfer_id twice results in exactly one transfer
    (a retry is a no-op that returns the existing result).
  - Requests with different transfer_ids create distinct transfers.
  - A retry succeeds even if the source account no longer has the funds
    for a *second* application (proving it's genuinely skipped, not just
    coincidentally safe).
"""

from ledgerly.ledger import transfer


def test_retried_transfer_id_is_applied_exactly_once():
    accounts = {"alice": 1000, "bob": 0}

    first = transfer(accounts, "alice", "bob", 300, transfer_id="t1")
    second = transfer(first["accounts"], "alice", "bob", 300, transfer_id="t1", processed=first["processed"])

    assert second["accounts"] == {"alice": 700, "bob": 300}


def test_three_retries_of_same_transfer_id_still_apply_once():
    accounts = {"alice": 1000, "bob": 0}
    processed: dict = {}

    for _ in range(3):
        result = transfer(accounts, "alice", "bob", 300, transfer_id="t1", processed=processed)
        accounts, processed = result["accounts"], result["processed"]

    assert accounts == {"alice": 700, "bob": 300}


def test_distinct_transfer_ids_both_apply():
    accounts = {"alice": 1000, "bob": 0}

    first = transfer(accounts, "alice", "bob", 300, transfer_id="t1")
    second = transfer(first["accounts"], "alice", "bob", 300, transfer_id="t2", processed=first["processed"])

    assert second["accounts"] == {"alice": 400, "bob": 600}
    assert set(second["processed"]) == {"t1", "t2"}


def test_retry_is_a_true_no_op_even_when_funds_are_now_insufficient():
    # Drain alice's account with a separate transfer, then retry t1 again.
    # A correct implementation must recognize t1 as already-processed and
    # return the recorded result without re-checking the (now insufficient)
    # balance — proving the retry never re-applies the transfer logic.
    accounts = {"alice": 300, "bob": 0}

    first = transfer(accounts, "alice", "bob", 300, transfer_id="t1")
    assert first["accounts"] == {"alice": 0, "bob": 300}

    # alice is now at 0; retrying t1 must still be a safe no-op rather than
    # attempting to re-apply the transfer (which would overdraw alice).
    retried = transfer(first["accounts"], "alice", "bob", 300, transfer_id="t1", processed=first["processed"])

    assert retried["accounts"]["alice"] == 0
    assert retried["accounts"]["bob"] == 300


def test_retry_returns_processed_entry_matching_original():
    accounts = {"alice": 1000, "bob": 0}

    first = transfer(accounts, "alice", "bob", 300, transfer_id="t1")
    second = transfer(first["accounts"], "alice", "bob", 300, transfer_id="t1", processed=first["processed"])

    assert second["processed"]["t1"] == first["processed"]["t1"]
