"""Visible tests for ledgerly.ledger — develop against these."""

import pytest

from ledgerly.ledger import InsufficientFundsError, transfer


def test_transfer_moves_funds_between_accounts():
    accounts = {"alice": 1000, "bob": 500}

    result = transfer(accounts, "alice", "bob", 300, transfer_id="t1")

    assert result["accounts"] == {"alice": 700, "bob": 800}


def test_transfer_does_not_mutate_input_accounts():
    accounts = {"alice": 1000, "bob": 500}

    transfer(accounts, "alice", "bob", 300, transfer_id="t1")

    assert accounts == {"alice": 1000, "bob": 500}


def test_transfer_rejects_overdraft():
    accounts = {"alice": 100, "bob": 500}

    with pytest.raises(InsufficientFundsError):
        transfer(accounts, "alice", "bob", 300, transfer_id="t1")


def test_transfer_allows_exact_balance_transfer():
    accounts = {"alice": 300, "bob": 500}

    result = transfer(accounts, "alice", "bob", 300, transfer_id="t1")

    assert result["accounts"] == {"alice": 0, "bob": 800}


def test_retried_transfer_id_applies_exactly_once():
    accounts = {"alice": 1000, "bob": 500}

    first = transfer(accounts, "alice", "bob", 300, transfer_id="t1")
    second = transfer(first["accounts"], "alice", "bob", 300, transfer_id="t1", processed=first["processed"])

    assert second["accounts"] == first["accounts"] == {"alice": 700, "bob": 800}


def test_different_transfer_ids_both_apply():
    accounts = {"alice": 1000, "bob": 500}

    first = transfer(accounts, "alice", "bob", 300, transfer_id="t1")
    second = transfer(first["accounts"], "alice", "bob", 200, transfer_id="t2", processed=first["processed"])

    assert second["accounts"] == {"alice": 500, "bob": 1000}
    assert set(second["processed"]) == {"t1", "t2"}
