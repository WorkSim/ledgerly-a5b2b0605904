"""Grading suite for LEDG-201 — transfer rejects overdrawing the source account.

Acceptance criteria:
  - A transfer exceeding the source account's available balance is
    rejected (raises InsufficientFundsError), not silently applied.
  - The source account is left untouched when a transfer is rejected.
  - Valid transfers within the available balance are unaffected, including
    a transfer that exactly exhausts the balance.
"""

import pytest

from ledgerly.ledger import InsufficientFundsError, transfer


def test_transfer_exceeding_balance_is_rejected():
    accounts = {"alice": 500, "bob": 100}

    with pytest.raises(InsufficientFundsError):
        transfer(accounts, "alice", "bob", 501, transfer_id="t1")


def test_rejected_transfer_leaves_accounts_untouched():
    accounts = {"alice": 500, "bob": 100}

    try:
        transfer(accounts, "alice", "bob", 999, transfer_id="t1")
    except InsufficientFundsError:
        pass

    assert accounts == {"alice": 500, "bob": 100}


def test_transfer_within_balance_still_succeeds():
    accounts = {"alice": 500, "bob": 100}

    result = transfer(accounts, "alice", "bob", 200, transfer_id="t1")

    assert result["accounts"] == {"alice": 300, "bob": 300}


def test_transfer_exactly_draining_balance_succeeds():
    accounts = {"alice": 500, "bob": 100}

    result = transfer(accounts, "alice", "bob", 500, transfer_id="t1")

    assert result["accounts"] == {"alice": 0, "bob": 600}


def test_transfer_one_cent_over_balance_is_rejected():
    accounts = {"alice": 500, "bob": 100}

    with pytest.raises(InsufficientFundsError):
        transfer(accounts, "alice", "bob", 501, transfer_id="t1")

    assert accounts == {"alice": 500, "bob": 100}


def test_zero_balance_account_rejects_any_positive_transfer():
    accounts = {"alice": 0, "bob": 100}

    with pytest.raises(InsufficientFundsError):
        transfer(accounts, "alice", "bob", 1, transfer_id="t1")
