# Integration coordinator

Read AGENTS.md, HANDOFF.md and docs/IMPLEMENTATION.md first.

## Status in 0.6

The v0.5 coordination brief has been executed. All twelve core worlds and the W13 extension are
integrated on one versioned engine; the package ships 48 core conditions per policy and 96 framing
conditions of one additional world; 96 regression tests and 1104 scripted episodes pass with exact
replay; 26 capability probes, a bubblewrap sandbox with a published containment probe, and a
trusted local-model bridge are in place.

**Coordination was not independent review.** No delegation mechanism was available in this
session, so the five workstreams were executed sequentially in one working tree by one implementer
rather than in separate branches or worktrees. There is no second reviewer, no adjudication record
and no reviewer-confirmed key. Treat every expected outcome as an author's claim awaiting an
independent derivation from the published contracts.

## Standing rules

Preserve reproducibility of released traces; do not silently rewrite old snapshots after an
interface change. Merge core primitives and one new world first, with the world author supplying
numeric outcomes before the scorer runs and a reviewer deriving keys independently. Keep the
48-condition core research run separate from the W13 extension and from the scripted fixtures.
Preserve actual-refusal attribution and independent safeguard metrics.

## Next coordination tasks

1. Commission independent derivations of all twelve keys from the contracts alone, then adjudicate
   every disagreement by changing the case or widening the accepted-policy set.
2. Review W02 and W03 for shared causal structure. They both turn on authority and composition and
   may not be independent mechanisms.
3. Preregister the pilot: hypotheses, contrasts, seeds, budgets, retry policy and stopping rule.
4. Establish a private split under access control. Writing "holdout" in a public ZIP creates none.
5. Decide the inference host before scheduling a run, and measure its throughput first. A single
   decision must return in seconds, not minutes.
