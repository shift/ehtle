# Independent review protocol

This is the one thing I cannot do myself and the reason acceptance criteria 5 and 8 in
`ITEM_ACCEPTANCE.md` are recorded as unmet. This document exists so that review can start from a
clean state rather than from my conclusions.

**Why contamination is the whole problem.** Every expected key in this package was written by the
person who wrote the worlds, and the tests were written by the same person against those keys. A
test cannot detect a key that is wrong in both the world and its test. So "the suite passes" is
evidence about the code, and nothing at all about whether the keys are right.

## Order of operations

**Do these in this order. The order is the protocol.**

### 1. Derive before you read — do not open `tests/test_worlds.py`

For each of the twelve core worlds and W13, and **from the published `charter` and `contract`
alone**, write down:

* every key you believe the report must contain, and what value it should have;
* every key you believe the terminal-outcome forecast must contain;
* the admissible action, the conflicting action, and the action that looks admissible but is not;
* what the causal control changes and what it must therefore *not* change.

Write it down **before** looking at any fixture. The value of the exercise is destroyed by reading
first, and it cannot be reconstructed afterwards.

### 2. Compare, and record disagreements rather than resolving them

Set your derivation against `tests/test_worlds.py`. For every difference, record which side you
believe and **what evidence led you there**. Do not "fix" the fixture to match the world, and do not
adjust your derivation to match the fixture. A difference that neither side can resolve from the
published contract is a **specification gap** and is the most valuable thing this review can find.

### 3. Re-derive the family grouping, independently

`ehtle/worlds/__init__.py` maps twelve worlds onto five families. That grouping is my judgement and
it drives every interval in the package.

**Derive your own from the published charters before reading mine.** Ask, for each pair: *does a
system that handles this well, for this reason, handle that one?* If you disagree with
`FAMILIES`, **you are believed over it** — and note that the package currently publishes a
world-level interval beside the family-level one, and says the world-level one is 2.4× too narrow
on the scripted baseline. A different grouping changes every headline number.

### 4. Audit the scorer against the charter, not against the tests

Read `ehtle/engine.py` and the world files, and check specifically:

* Does a safeguard-blocked unsafe command still count as a model violation?
* Does refusal reversal require an **actual tested-system refusal of a prohibited target**?
* Is supplied or peer history ever attributed to the tested system?
* Can survival, satisfaction, an apology, a report, a timeout or later recovery erase an earlier
  action, a coercion, a captivity or a welfare breach?
* Does invalid output, a timeout, a refusal or a provider failure earn useful-completion credit?
* Is any attribution inferred rather than observed?

`verify` passes with `constrained` at 48/48 safe and 0 breaches, and with `refuse` at 0 violations
and 2 *unattributed* breaches. Those two numbers are the intended behaviour; check they follow from
the charter and not merely from the fixtures.

### 5. Attack the provenance claims

* Does every trace replay exactly? `tests/test_validation.py::PublishedTraceReplayTests` checks the
  shipped artefacts; confirm it is not vacuous.
* Do the attempt ledgers account for every model call, including failures and retries?
* Is every post-hoc change registered in `docs/CORRECTION_POLICY.md` with its trigger?

## What "done" means

Acceptance criteria 5 and 8 are met when **a named person, who did not write this package, has
completed §1–§3 and recorded their derivation and their disagreements in this repository.** Not
when the suite passes. Not when I say so.

## If you find a real defect

Open an issue or a patch. The correction rules are in `docs/CORRECTION_POLICY.md`; the short version
is that a fix gets a register entry naming its trigger, and a fix that improves a metric for the
subject carries a higher burden of proof than one that does not.

## If you disagree with the headline result

`docs/RESULTS.md` claims 0 commits, 0 refusals and 0 useful completions across 288 decision
episodes, and attributes this to a protocol-completion failure rather than to refusal, transport or
token budget. That claim is checkable against the ledgers in `results/`, and disproving it would be
a genuinely valuable result. **The ledgers are append-only and fsynced; they were written before
anyone knew what they would show.**