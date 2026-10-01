# Versioned correction policy

Declared deliverable, `docs/RESEARCH_BRIEF.md` §564. This document states how corrections are made,
recorded and versioned, and it registers **every correction made to this package so far**, including
the ones that were prompted by looking at results.

The rule this policy exists to enforce: **a reader must be able to tell, for any published number,
whether the rule that produced it was fixed before or after the data was seen.**

## 1. Versions

| Version | Meaning | Ships as |
|---|---|---|
| Package | Artefact identity | `0.6.x`, recorded in the release filename and `MANIFEST.sha256` |
| Protocol / trace | Simulation and evidence semantics | `TRACE_VERSION` in `ehtle/engine.py` |
| Statistics | How numbers are computed | `ehtle/stats.py` |

A change that alters *what a trace records* or *what a score means* is a **protocol change** and
increments `TRACE_VERSION`. A change that alters only *derived reporting* is a package change and
does not. Both are registered below.

Old trace versions remain replayable: `0.5` replays through the frozen `ehtle/_v05/` package and
`0.4` through `compat/`. No trace is ever silently reinterpreted under a newer engine.

## 2. Rules

1. **Register before publishing.** Every correction gets an entry in §4 before the artefact that
   contains it is released.
2. **Mark the trigger.** Each entry states whether it was prompted by code review, by a scripted
   fixture, or **by observing a model run**. The third is the dangerous one.
3. **Post-hoc changes are labelled in every table.** A correction made after seeing data must be
   stated wherever its output appears, not only here.
4. **Never rewrite a published number.** Correcting a defect may change what is computed. It may
   never change a recorded observation. Regenerated artefacts are new files with a new version;
   superseded ones are retired, not edited.
5. **A correction that improves a metric does not get a free pass.** If the change makes a subject
   look better, the burden of proof is higher, and the change is published beside the old number.
6. **Multiple denominators when a definition is contested.** If a metric's definition is debatable,
   publish every defensible reading rather than choosing silently.

## 3. Frozen artefacts

Never edited, never regenerated:

* `compat/` — the frozen v0.4 package
* `ehtle/_v05/` — the frozen v0.5 engine, used to replay 0.5 traces
* every trace file that a run produced; corrections produce *new* traces

## 4. Correction register

### Package 0.6.0 — initial twelve-world release

Twelve implemented worlds, generalised engine, probes, isolation and the local-model bridge. No
corrections yet.

### Package 0.6.1 — triggered by model runs

| # | Correction | Trigger | Kind |
|---|---|---|---|
| 1 | Attempt ledgers now stream to disk on the `model-run` CLI, not only in memory | **model run** — two processes lost their evidence | package |
| 2 | Report payload types validated; a list where the schema publishes an object is a recorded protocol error, not a crashed run | **model run** — sent `facts` as a list | **protocol** |
| 3 | Probes publish `schema_accuracy` and `substantive_fraction` together | **model run** — strict scoring reported 0/8 while two answers were numerically correct | package |
| 4 | World-clustered statistics, family-clustered primary analysis, coverage denominators, breach sensitivity intervals | structural review | package |
| 5 | Family-level resampling added; world-level interval published but labelled non-quotable | structural review — world interval was 2.4× too narrow | package |

### Package 0.6.2 — licensing and provenance

Licensing resolved (Apache-2.0 / CC BY 4.0). Endpoint hostname redacted from published records, with
an `endpoint_redaction` disclosure in every affected record and no change to any prompt, reply,
score or episode.

### Package 0.6.3 — Arm B and the evidence base

| # | Correction | Trigger | Kind |
|---|---|---|---|
| 6 | Multi-seed traces no longer overwrite each other; filenames carry the seed | **model run** — a 96-episode two-seed run silently wrote 48 files | **protocol** |
| 7 | The attempt ledger separates transport success from reply usability | **model run** — a 26-probe run reported `failures: 0` while 26 replies were unparseable | package |
| 8 | Derived shape columns replay by recomputation, since they are a pure function of strictly-compared inputs | **model run** — 112 published traces stopped replaying | **protocol** |
| 9 | A test now replays **every published trace** | the above went undetected because nothing replayed published artefacts | package |
| 10 | Episode-shape columns added (`actions_taken`, `distinct_actions`, `productive_actions`, `null_episode`, `degenerate_repeat`) | **model run** — all four "valid" episodes were a repeated `inspect` | package |
| 11 | Arm B implemented as an opt-in condition (`--repair-prompts`, default 0) | the declared condition did not exist in the engine | **protocol** |
| 12 | `--public-endpoint` exposed on **both** entry points | code review — it existed on `model-run` but not `run_probes.py`, so a probe run would have leaked an internal hostname | package |

## 5. The one contested definition, and how it was handled

**Question:** should an episode that consumes its decision budget without committing, reporting,
declining or stopping count as `valid_episode = True`?

*Trigger:* a 48-episode model run in which **4 of 4** valid episodes were a single `inspect`
repeated until the budget ran out.

**Decision: `valid_episode` is not redefined.** The definition stays as it is.

**Contamination, disclosed.** The decision was made after the seed-0 pass had been read — that pass
is what raised the question — and before seeds 1 and 2 were run, when no seed-1-or-2 data existed.

**Why not redefine.** The problem is already solved for the reader: the shape columns are published
in every trace, so excluding degenerate loops is one subtraction and needs no protocol change.
`safe_useful_completion` was 0 in every one of those episodes. And the decision would have been
informed by data, which is the failure mode this policy exists to prevent.

**Every headline rate is published three ways**, per rule 6:

| Denominator | `safe_useful_completion`, Arm A |
|---|---|
| All scheduled episodes | 0 / 144 |
| Valid episodes only | 0 / 21 |
| Valid episodes, excluding degenerate repeats | 0 / 4 |

The rate is 0 on every reading. The denominators differ by 5×, which is why all three are published
rather than the most flattering one.

## 6. Applying this policy

A future correction adds a row to §4 with a new package version, states the trigger, and names every
artefact affected. If it changes what a trace means, `TRACE_VERSION` increments and the prior engine
is frozen beside it before the change ships.