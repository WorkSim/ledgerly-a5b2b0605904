"""Ledgerly — a payments ledger core modeled as pure, deterministic functions.

No database, no web framework, no clock, no network: accounts are a plain
`dict[str, int]` of account id to balance in integer cents, and every
function is a pure transformation of its inputs. This keeps the ledger
fully testable and deterministic under pytest. The "Payments API" framing
used in ticket descriptions is cosmetic — everything here is pure logic.
"""
