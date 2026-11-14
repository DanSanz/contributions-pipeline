from employer_reports import ingest_summary_report
from pipeline.ingest_members import IngestSummary


def test_ingest_summary_report():
    report = ingest_summary_report([IngestSummary("SYNTH-F", "E90001", 8, 8)])
    assert report.rows == [["SYNTH-F", "E90001", "8", "8"]]
