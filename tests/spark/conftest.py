"""One SparkSession for the slow suite: local[1], no UI.

Keep these tests in memory. Build frames with createDataFrame and check them with collect();
don't write files through Spark (df.write fails on laptops without winutils.exe).
"""

import pytest

from pipeline.spark import get_spark


@pytest.fixture(scope="session")
def spark():
    session = get_spark("contributions-pipeline-tests", master="local[1]")
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()
