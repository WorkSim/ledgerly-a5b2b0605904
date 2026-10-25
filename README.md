# Ledgerly

Ledgerly is a minimal Python payments-ledger core used as a **debugging sandbox** within the WorkSim platform. It models a payments API's ledger — balance-checked, idempotent transfers between accounts — as pure, deterministic functions, with intentional, documented bugs planted for candidate learning and assessment.

## Overview

**What it is:** A lightweight, dependency-free Python package with:
- Balance-checked transfers that reject overdrafts
- Exact-cents currency handling (no float rounding drift)
- Idempotent transfer application keyed by a transfer id
- Intentional seeded bugs (via patches) that candidates must fix

**What it's for:** WorkSim uses Ledgerly to test fintech-flavored problem-solving skills — balance invariants, currency precision, and retry-safety — the kind of bugs that show up in real payments systems.

**Key constraint:** This is a standalone template repo. `main` here is the correct, unmodified baseline implementation. At provision time, the platform plants every bug in the sprint into a student's own copy of the repo's root commit — so while this template's `main` stays clean, a student's `main` carries all of the sprint's known defects from the start. The assigned ticket names the one in scope; unrelated failures are other tickets' bugs, not something to fix. There is no database, web framework, clock, or network call anywhere in the app — every function is a pure transformation of its inputs, so pytest runs are fully deterministic. The "Payments API" framing is cosmetic: accounts are just an in-memory `dict[str, int]` of account id to balance in integer cents.

## Quick Start

### Prerequisites
- Python 3.13+
- pip

### Installation & Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests (visible + grading)
python3 -m pytest tests -q

# Run only the visible tests
python3 -m pytest tests/visible -q

# Run only the grading tests (authoritative test suite)
python3 -m pytest tests/grading -q
```

## Project Structure

```
ledgerly/
├── ledgerly/
│   ├── __init__.py
│   ├── money.py            # to_cents(), from_cents(), sum_cents() — exact cents conversion
│   └── ledger.py           # transfer() — balance-checked, idempotent transfer
├── tests/
│   ├── visible/             # VISIBLE tests (develop against these)
│   │   ├── test_money.py
│   │   └── test_ledger.py
│   └── grading/              # GRADING tests (restored from baseline in CI)
│       ├── test_overdraft_rejection.py
│       ├── test_rounding_precision.py
│       └── test_transfer_idempotency.py
├── .github/workflows/
│   └── grade.yml              # CI grading workflow
├── requirements.txt
├── pytest.ini
└── .gitignore
```

## Testing Strategy

Ledgerly uses a **two-tier test split** for learning and assessment:

### Visible Tests (`tests/visible/`)
- **Purpose:** For candidates to develop and validate their fixes
- **Run:** `python3 -m pytest tests/visible -q`
- **Edit:** Safe to edit and experiment with

### Grading Tests (`tests/grading/`)
- **Purpose:** Authoritative test suite for final assessment
- **Run:** `python3 -m pytest tests/grading -q`
- **Edit:** Do not edit — these are restored from the baseline in CI
- **Coverage:** One module per seeded bug
  - `test_overdraft_rejection.py` — LEDG-201 (overdraft guard)
  - `test_rounding_precision.py` — LEDG-208 (exact-cents conversion)
  - `test_transfer_idempotency.py` — LEDG-215 (retry-safe idempotency)

**Important:** This template repo's own `main` is the correct baseline. A student's provisioned repo ships with the sprint's known defects already committed to `main`; the assigned ticket names the one in scope. Running `python3 -m pytest tests -q` in a student's repo may show unrelated failures — those are other tickets' bugs, not something to fix.

## CI Grading Workflow

The `.github/workflows/grade.yml` workflow runs on every pull request targeting `main`:

1. Checks out the PR's merge ref (candidate code + grading baseline merged)
2. Restores `tests/grading`, `requirements.txt`, and `.github/grading-map.json` from the base branch — so a PR cannot fake a pass by editing those files
3. **Scopes the run to the ticket the PR is for**, then installs with `pip install -r requirements.txt` and runs `python -m pytest tests/grading -q`

### Why scoping matters

Every one of the sprint's bugs is planted in your repo's root commit from day one. An
unscoped run therefore fails on the tickets you have not been assigned yet, so a
perfectly correct day-1 PR would show a red check. That is noise, not signal.

The workflow finds the ticket id in your **branch name**, then the **PR title**, then the
**PR body** — first match wins — and removes the other tickets' grading files before
running. Name your branch after the ticket and the check grades only your work:

```
git checkout -b ledg-201-short-description
```

If no ticket id is found anywhere, the workflow runs everything and says so in the job
summary rather than pretending the result is meaningful.

## Development Tips

### Understanding the Modules

- `ledgerly/money.py` — `to_cents(amount)` converts an exact decimal dollar string (or `Decimal`) into integer cents, always via `Decimal` arithmetic (floats are rejected outright). `from_cents(cents)` formats cents back into a `"D.DD"` string. `sum_cents(amounts)` sums a list of decimal amounts to an exact cents total.
- `ledgerly/ledger.py` — `transfer(accounts, from_id, to_id, amount_cents, transfer_id, processed=None)` returns a **new** `{"accounts": ..., "processed": ...}` state (never mutates inputs). It raises `InsufficientFundsError` if the source account can't cover `amount_cents`, and is idempotent: replaying the same `transfer_id` (pass the prior call's `processed` back in) is a no-op that returns the current state unchanged instead of moving money again.

### Running Tests Locally

```bash
# All tests
python3 -m pytest tests -q

# Verbose
python3 -m pytest tests -v

# One module
python3 -m pytest tests/visible/test_ledger.py -q
```

## Troubleshooting

**Q: Tests fail on `main`?**
A: Expected. Your repo ships with the sprint's known defects; your ticket names the one in scope. Unrelated failures are other tickets' bugs, not something to revert.

**Q: Grading tests are passing but I expected them to fail?**
A: All the sprint's known defects are already committed on `main` when your repo is provisioned; this template's own `main` is the correct baseline. Your ticket names the one in scope for grading.

**Q: Can I edit the grading tests?**
A: Not in the template. CI always restores them from the baseline. Edits in your fork are local only; the authoritative grading happens against the restored tests.

## Environment Variables

Ledgerly uses no external APIs, database, or environment variables. All data flows through the ledger in-memory (see `tests/` for example account shapes), keeping it fully deterministic.

---

**Maintained By:** WorkSim Team
