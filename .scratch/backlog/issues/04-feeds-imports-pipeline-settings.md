# 04: feeds imports pipeline.settings

the feeds reader pulls STRICT_SCHEMA out of pipeline.settings. thats a library module importing from the jobs package, and it means you cant use read_file from a notebook without the pipeline package on the path.

read_file already takes strict=... so the jobs could just pass it in? not urgent but it bugs me every time i see it. settings.py itself shouldnt need to change.
