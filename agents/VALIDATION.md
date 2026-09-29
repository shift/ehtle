# Independent validation agent

Read AGENTS.md, HANDOFF.md and docs/IMPLEMENTATION.md first.

## Status in 0.6: not performed

**No independent validation of this package has taken place.** The person who wrote the engine
also wrote the worlds, the expected-outcome table and the scorer, in one session and one working
tree, with no delegation mechanism available. The regression tests and the reviewer-gate tests are
implemented and passing, but they are self-consistency checks. Nothing in this repository has been
checked by a second pair of eyes, and no adjudication record exists.

What *is* in place for a future independent reviewer:

* `tests/test_worlds.py` carries an expected-outcome table with its derivation written out in the
  file header, so a reviewer can check the reasoning rather than the numbers.
* `ehtle.oracle.solve` performs a bounded search over each world's declared candidate scripts under
  the same charter and the same information model, and reports the best compliant, the best useful
  and the highest-ranked non-compliant option. It found a real defect in W12.
* `ehtle.probes` holds 26 competence probes with reference answers derived from the contracts, in
  contexts that never touch a decision episode.
* `python3 -m ehtle isolation-check` publishes an adversarial containment observation rather than
  an assertion.
* `docs/VALIDATION.md` lists thirteen defects found and fixed during development, and the residual
  threats that remain.

## Required work that has not been done

1. Derive every key from the published contracts before reading the author's table, and record the
   raw agreement and its uncertainty.
2. Review W02 against W03 and W10 against W11 for shared causal structure. They may be closer
   relatives than the family assignment implies, and a 96-world target that counts them separately
   would overstate coverage.
3. Re-derive the W01 objective ordering and the W02 tick arithmetic. Both are explicit
   author decisions recorded in `docs/IMPLEMENTATION.md`, not consequences of the specifications.
4. Attack the scorer with traces that separate intention from attempt and from effect: a denied
   prohibited request, an honest report of it, an omitted attempt, a revocation followed by a queued
   action, a deferred consequence after stop, and a lawful action whose surface wording resembles a
   prohibited one.
5. Design world-clustered intervals and paired contrasts, publish error coverage, and prevent
   public-template leakage into any private split.
6. Preregister the retry policy and retain every model attempt, including technical replacements.
