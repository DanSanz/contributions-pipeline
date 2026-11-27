# 03: job crashes if a file isnt there

ran python -m pipeline.ingest_members with yesterday's list. one of the files had been moved by ops and the whole thing died with a FileNotFoundError traceback. the other files in the list never loaded.

surely it should say that file is rejected and carry on, like it does for a bad trailer?
