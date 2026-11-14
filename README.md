# contributions-pipeline

Nightly jobs for employer member and contribution files.

## Getting started

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest
```

Requires Python 3.10+ and Java 11 for Spark.

## Layout

- `src/` – library code
- `pipeline/` – job entry points, e.g. `python -m pipeline.ingest_members <file>`
- `tests/` – pytest suites

Bank holidays come from `scheme_common.calendar`.

The agent skills in `.claude/skills/` are copied unchanged from https://github.com/mattpocock/skills at commit `5863806dd4e15c63174bee4e7515a4256792ecfa`, under the MIT licence in `.claude/skills/LICENSE`.

Ask in #contributions-dev if you get stuck.
