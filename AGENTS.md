## Build and test

Run `powershell -File scripts\check.ps1`; add `-Spark` to include `tests/spark` (slow, needs Java). The README's `python -m pytest` fails at collection: it picks up `tests/acceptance`, which the check script leaves out.

## Standards

Before writing or reviewing code, tests, commits or PRs, read `docs/standards.md`.

## Runbook

Before changing or running a nightly job in `pipeline/`, read `docs/runbook.md`.

## Domain terms

Before naming a domain concept in code, tests, issues or commits, read `GLOSSARY.md` and use its terms. Where the runbook or README words differ, the glossary wins.

## Agent skills

### Issue tracker

Issues live as markdown files under `.scratch/<feature>/` in this repo. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default role names (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), recorded as a `Status:` line in each issue file. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
