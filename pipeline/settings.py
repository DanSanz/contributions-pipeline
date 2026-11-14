"""Settings shared by every feed job: members, contributions and the valuation extract.

A change here changes every employer feed at once. Changes need a Technical Lead's review
(see CODEOWNERS); don't change a value here to make one job or one test pass.
"""

import os
from pathlib import Path

# Reject detail records with more fields than the feed contract defines.
STRICT_SCHEMA = True

# Service account recorded as the actor on audit events raised by the batch jobs.
AUDIT_ACTOR = "svc-contributions-pipeline"

# Local runs. Production sets these through the environment.
LOCAL_DIR = Path(os.environ.get("CP_LOCAL_DIR", "local"))
MEMBER_DB_PATH = LOCAL_DIR / "members.sqlite"
AUDIT_LOG_PATH = LOCAL_DIR / "audit.jsonl"
VALUATION_EXTRACT_URI = os.environ.get("CP_VALUATION_EXTRACT_URI", "")

# Spark master for the jobs. Tests always use local[1].
SPARK_MASTER = os.environ.get("CP_SPARK_MASTER", "local[1]")
