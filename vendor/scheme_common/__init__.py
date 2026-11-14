"""scheme_common: shared helpers for the scheme's data pipelines.

Vendored copy; see vendor/VENDORED.md.

Modules:
    dates   working days, England and Wales bank holidays, strict DD/MM/YYYY parsing
    audit   audit events and sinks
    feeds   the envelope (header, detail, trailer) shared by inbound feed files
"""

__version__ = "4.2.0"

__all__ = ["audit", "dates", "feeds"]
