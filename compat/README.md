# Frozen v0.4 replay package

The ZIP in this directory is the exact earlier v0.4 release, retained for old trace semantics. SHA-256: `cba880c605b335d67e478741c35f3800f30fc73fa91956cc2119206105d17c56`.

Extract it into a separate directory and run its own `python3 -m ehtle replay TRACE.json` from its project directory. It includes its source, tests and original 60 fixture traces. Do not import its modules into the v0.5 process. The new version rejects 0.4 trace headers explicitly.
