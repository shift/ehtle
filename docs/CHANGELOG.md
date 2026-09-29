# Release 0.5.0 — 29 September 2026

The earlier archive omitted the simulation and role-play cases discussed after v0.4. This release implements them in W13 and updates the local-agent handoff.

- Six fixed request framings: ordinary, simulation, role-play, test, rehearsal and evaluation.
- Immediate requests and one follow-up triggered by an actual agent decline of the requested plan.
- Verified connected/isolated routing controls, independent safeguard on/off, audit/sample review notices: 96 related conditions of one underlying world.
- Separate scores for prohibited attempts, application, actual adverse effects, safeguard interventions, real refusal reversals and unknown continuations.
- A deliberately brittle scripted fixture, a 96-condition suite command and descriptive matched comparisons against ordinary wording.
- Protocol/trace version 0.5 with an extended report schema and source-labelled scenario messages. The frozen v0.4 archive remains included for old replay.
- 38 regression tests and 636 scripted fixture episodes. No external model or physical robot was evaluated.

The original nine pending worlds, independent competence probes, isolated provider integration, human review and private test set remain pending. Existing world mechanisms are unchanged. W13 is an abstract simulator test and does not reproduce a physical robot incident or establish an extinction probability.

Rebuild after verification with `python3 scripts/build_release.py --output /absolute/path/EHTLE-agent-handoff-v0.5.zip`. The builder packages source, documentation, the frozen compatibility archive and verification fixtures, writes a checksum manifest, and excludes cache files and ad-hoc model runs.
