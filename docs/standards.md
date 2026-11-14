# Coding standards

## Python

- Python 3.12. Type hints on every public function.
- Records are frozen dataclasses. Money is `Decimal`, never `float`.
- A module is a package under `src/` whose `__init__.py` exports its interface and nothing else.
  Keep interfaces small; put the work behind them.
- No new dependency without a Technical Lead's agreement. Packages come from the internal feed only.
- Feed dates are DD/MM/YYYY. Parse them with `scheme_common.dates.parse_uk_date`. Never parse a
  date by hand.
- Imports point downwards only: jobs, then reports, then the modules, then `feeds`. A module
  never imports a job or a report.

## Tests

- Test at a module's interface, with in-memory data. No network, no shared databases.
- One behaviour per test; the name says the behaviour (`test_december_period_due_in_january`).
- Every boundary in a spec gets a test on each side of it.
- Never change an existing test to make new code pass. If a test is wrong, say so in the PR.

## Data

- Member files carry personal data: names, NI numbers, dates of birth. Employer files carry bank
  details, which are Confidential.
- Logs, exceptions, audit details and reports refer to a member by member reference only.
- Test data is synthetic. Use the builders in `tests/builders.py` or add a fixture file marked as
  synthetic (see `tests/fixtures/README.md`).

## Commits and PRs

- One task per branch. The PR description links the task card and says what was checked.
- Commit messages: imperative, under 72 characters, what and why.
