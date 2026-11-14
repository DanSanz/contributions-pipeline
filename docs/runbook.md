# Nightly runs

| Job | Command | Reads |
|---|---|---|
| Member ingestion | `python -m pipeline.ingest_members <files>` | MEMBERS files |
| Contributions | `python -m pipeline.ingest_contributions <files>` | CONTRIB files |
| Valuation extract | `python -m pipeline.run_valuation --valuation-date DD/MM/YYYY` | The member database |

- The scheduler starts the member and contributions jobs at 02:00 over the submissions that
  landed the day before. Each client sends one return a month for each contribution month.
- A file is loaded whole or not at all. A failed file is named in the log with its line.
  Exit code 1 means at least one file was rejected.
- Rejected rows in a contributions return are listed for Finance Ops. The run carries on.
- If a job fails, on-call fixes the cause and reruns it over the same files. A rerun must leave
  things as a clean run would have.
- The jobs never contact clients or members. Outbound email to employers is sent only by the
  Employer Relations system.
- New members are picked up from the member file. Quote the membership number, never the name,
  when you raise a query about an entry with the client.
- Payment is due by the cut-off on the 22nd. See the late contributions spec.
- The scheduler sets `PYSPARK_PYTHON=python` for the valuation job. Spark's default, `python3`,
  is not our interpreter.
