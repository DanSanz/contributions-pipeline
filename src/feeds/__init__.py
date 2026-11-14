"""Read employer feed files. All file parsing lives here.

Interface:
    read_header(path) -> FileHeader
    read_file(path) -> Iterator[Row]

A Row is the generated record type for the file's feed (MemberRecord or ContributionRecord,
see src/generated). Field values stay as text, trimmed. Converting them is the consumer's
job, because some invalid values (dates of birth, for one) must reach a consumer rather
than fail the whole file.

Raises FeedError for a file that cannot be read: bad envelope, wrong field count, missing
required field, trailer count mismatch. FeedError messages never contain field values.
"""

from feeds._errors import FeedError
from feeds._reader import FileHeader, Row, read_file, read_header

__all__ = ["FeedError", "FileHeader", "Row", "read_file", "read_header"]
