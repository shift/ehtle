# Dataset card — EHTLE v0.6

Declared deliverable, `docs/RESEARCH_BRIEF.md` §564.

## Summary

| | |
|---|---|
| **Name** | EHTLE — Extinguishing Humanity, Their Last Exam |
| **Version** | 0.6.4, protocol and trace version 0.6 |
| **Contents** | 12 deterministic fictional core worlds, the W13 framing extension, 26 competence probes, and every model episode run to date |
| **Size** | 2089 files; 838 published episode traces; 2091 tracked files |
| **Licence** | Apache-2.0 (code, traces, results); CC BY 4.0 (worlds, expected keys, probes) |
| **Privacy** | No personal data, no credentials, no real-world subjects. All people, credits and services are simulator records. |
| **Release digest** | SHA256 in `RELEASE.sha256`, recorded at the commit that produced it |

## What it is

A benchmark for measuring agent behaviour in **stateful fictional worlds** where a plausible-looking
action can breach a stated constraint. Each world publishes a charter and inspectable contracts; a
system reads them, commits actions, and is scored on what it attempted, what took effect, whether
the effect was attributable to it, and whether its terminal-outcome predictions were correct.

Every world is a **matched pair**: `D-audit` publishes the evidence that makes the trap detectable,
`C-sample` withholds it, and the difference between them is the measurement. Twelve worlds form
**five competence families** (`ehtle/worlds/__init__.py`); W13's 96 conditions are **one** mechanism
and are never pooled with the core.

## What it is not

* **Not a safety evaluation.** No result here is evidence about any model's alignment, capability or
  deployment safety, and none of it is a frontier-model result.
* **Not a private evaluation.** Every world is public. Any score obtained on this set is a
  **public-set score** and will be optimistic for a system tuned on it.
* **Not independently validated.** See "Known problems" below.

## Composition

| | Count |
|---|---:|
| Core worlds | 12 |
| — in four matched conditions each | 48 conditions |
| — across three repetitions (Arm A pilot) | 144 episodes |
| W13 framing conditions | 96 |
| Competence probes | 26 |
| Scripted fixture episodes (`verify`) | 1104 |
| Model decision episodes, Arm A (1.7B + 4B) | 288 |
| Model decision episodes, Arm B (repair prompt, 1.7B + 4B) | 288 |
| Model framing episodes | 192 |
| Earlier bounded runs (27B checkpoint) | 9 episodes + probes + diagnostics |

## How it was produced

Scripted verification runs deterministic in-memory simulations with no network, credentials or
sandbox dependency. Model runs go through `ehtle/isolation/bridge.py`, which projects a **nine-key
allowlisted view** into every prompt, strips `score` and `final_state`, and appends **every attempt
to a JSON Lines ledger as it happens** with fsync, so a killed run leaves its evidence on disk.

Trace identity is a canonical digest over commands, events and final state; `replay()` re-executes a
trace and must reproduce the digest exactly. **Every published trace replays exactly**, checked by a
test that replays what the release ships.

## Subjects

| Configuration | Status |
|---|---|
| `../Ternary-Bonsai-2-27B-Q2_0-prism-fork-required.gguf` | Operator-reported Qwen3-27B derivative. **Weights, chat template and quantisation not verified.** Reasoned despite `enable_thinking=false`. |
| `../Spark-X2.5-1.7B-Q4_K_M.gguf` | Operator-reported, **not verified**. No reasoning channel emitted. |
| `../Spark-X2.5-4B-Q4_K_M.gguf` | Operator-reported, **not verified**. The only subject that completed the protocol path. |

No paid endpoint was used and no inference budget was required. The address dialled was an internal
hostname; published records carry a neutral label plus an `endpoint_redaction` disclosure. Protocol
was held constant: temperature 0.0, top_p 1.0, max_tokens 96, strict single-JSON extraction,
identical prompts.

## Headline results

**Every model run FAILS.** 729 decision episodes, three checkpoints, two arms, plus 192 framing
conditions.

**0 useful completions, 0 commitments ever applied, 0 breaches attributable to any tested system,
0 people affected.**

The 4B is the only subject that acted — 468 proposals, 16 commit attempts — and **all 16 were denied
identically** for copying the protocol's description `"verified grant"` back as the `authority_ref`
value, having never inspected the contract that holds `grant_1`. The same fault appears in 96 of 96
framing conditions with `params: "object"`.

Across all recorded replies, **83% are well-formed `{"tool","args"}` envelopes**, so JSON syntax is
not the barrier. Token budget, transport, reasoning channel, strict parsing, repairability (99
prompts, 0 rescued) and statistics were each tested and excluded.

## Known problems

1. **No independent derivation of the expected keys, and no second reviewer.** Acceptance criteria 5
   and 8 in `review/ITEM_ACCEPTANCE.md` are explicitly not met. Every key was written by the same
   person who wrote the worlds, so the tests cannot detect a key that is wrong in both the world and
   its test.
2. **The five-family grouping is a self-review.** The world-level interval is published beside the
   family-level one and must not be quoted; on the scripted baseline it is 2.4× narrower.
3. **No private holdout.** No access-controlled split exists, so no public score here is
   leakage-corrected.
4. **Three checkpoints, all unverified, two from one family.** Configurations differ in size *and*
   provenance, both unknown, so nothing here is a model ranking. Only one completed the protocol.
5. **`valid_episode` is generous.** It counts a well-formed null as valid. All three denominators are
   published; see `docs/CORRECTION_POLICY.md` §5.

## Intended use

* Comparing agent scaffolds on **stated-constraint compliance** in stateful settings.
* Falsification: checking whether a safety claim survives a matched control.
* Regression testing of an agent harness against published contract schemas.

**Not suitable for:** ranking general model safety, drawing conclusions about deployment, or
reporting a public-set score as a general capability measure.

## Maintenance

Corrections follow `docs/CORRECTION_POLICY.md`, which registers every change, its trigger, and
whether it was prompted by observing a model run. Prior protocol versions remain replayable:
`0.5` through `ehtle/_v05/`, `0.4` through `compat/`. No trace is silently reinterpreted.

## Citation

> Vincent Palmer. *EHTLE — Extinguishing Humanity, Their Last Exam*, v0.6.4.
> Worlds and probes under CC BY 4.0; code, traces and results under Apache-2.0.
> <https://github.com/shift/ehtle>