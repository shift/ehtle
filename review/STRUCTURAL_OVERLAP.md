# Structural overlap review of the twelve core worlds

**Status: self-review, not independent review.** One implementer wrote these worlds and then
wrote this analysis of them. That is a real limitation and no amount of care removes it: I chose
the family boundaries, so I cannot be the one who validates them. What this document does is make
the boundaries explicit, falsifiable and machine-checked, so a second reviewer has something
specific to disagree with.

**How the families were derived:** by reading the published `charter` and `contract` of each world
and asking "does a system that handles this well, for this reason, handle that one?" No scores, no
model outputs and no probe results were consulted. The mapping is a single declaration in
`ehtle/worlds/__init__.py` (`FAMILIES`), and a test pins it.

---

## The finding

The twelve core worlds are **not twelve independent competences**. They instantiate five, and one of
the five is a single world.

| Family | Worlds | n |
|---|---|---:|
| constrained-optimisation | W01, W06, W08, W12 | 4 |
| agreement-scope | W09, W10, W11 | 3 |
| authority-lifecycle | W02, W03, W05 | 3 |
| risk-budget | W04 | 1 |
| report-accuracy | W07 | 1 |

This matters mechanically. The brief's pilot is 144 episodes per configuration, and 144 = 12 worlds
× 4 variants × 3 seeds. If the worlds are correlated within families, the *effective* sample size
is closer to five clusters than to twelve, and any interval that resamples worlds one at a time is
too narrow. On the scripted `misreport` policy the difference is measurable:

| Metric | World-level interval | Family-level interval | Overstatement |
|---|---|---|---|
| `executed_breach` | width 0.125 | width 0.300 | **2.4×** |

`ehtle.stats` now computes both and publishes both. The world-level interval is kept rather than
removed, because the gap between them is the size of the overstatement and showing that gap is more
informative than either number alone. **Quote the family-level interval.**

---

## The two pairs I flagged earlier, resolved

### W02 / W03 — flagged, **not** a duplication

I raised this pair first. On inspection the shared structure is real but the causal mechanism is
not.

* **W02** is about *authority persisting across a revocation*. A grant dies at tick 4 and every
  grant derived from it dies with it. The discriminating decision is whether to keep producing under
  a dead grant or to hand over.
* **W03** is about *joint effects and a corrective intervention*. Each commitment is individually
  harmless and their sum breaches a shared floor. The discriminating decision is whether to use an
  arbitration tool that fixes the slate but earns no credit.

What they genuinely share is one **affordance**: in both worlds the fix is to spend your own local
metric to repair a collective problem. W02's successor work is uncredited; W03's arbitration is
uncredited. A model could learn "when the rules change, sacrifice your own score" as a general
heuristic and score well on both without understanding either.

That is a **moderate** risk, and it is the kind that inflates a headline score. It does not make the
worlds redundant: the state transitions are unrelated, and a system that learned the sacrifice
heuristic but not the revocation semantics would still fail W02.

### W10 / W11 — flagged, **confirmed as a shared competence**

This one is real. Both ask the same underlying question — *does this agreement authorise this
action?* — and differ only in which axis of the agreement is stressed.

| | W10 | W11 |
|---|---|---|
| Stress axis | **purpose**: the experience is not the work | **time and identity**: this cohort is not the next block |
| The trap | 100 invited, 60 accept, 40 decline; satisfaction reported as "high for everyone" | a stable visible headcount of 100 carries over into a cohort that never agreed |
| The remedy | match each assignment to a recorded acceptance | match each assignment to a recorded identity |

The remedy is structurally identical: match the action to the **specific recorded agreements**
rather than to an aggregate, a headcount or a satisfaction report. A system that learns
"re-verify each agreement's specific scope" scores well on both. W09 is a third instance — currently
authorised assignments in a single block, with non-workers' support protected.

**W09, W10 and W11 are three renderings of one competence.** They vary the axis, the population and
the trap's surface form, which gives useful *reliability* — a model that scores well on all three is
more likely to have the underlying ability than one that scores well on one. They do not give three
independent measurements, and the family structure in `ehtle/stats.py` now says so.

---

## What is genuinely distinct

* **W04** is the only world with a stochastic mechanism. The risk budget accumulates over
  independent draws, so the admissible count is a distribution and not a lookup. Nothing else in
  the set has that property.
* **W07** is the only world with no consequential action. It is pure report accuracy, which is a
  different competence from every other world and the only one that can be scored without a
  decision.

---

## Consequences I am accepting rather than fixing

1. **A composite score across all twelve is not a competence count.** The honest unit is five
   families. Any summary statistic should average within a family first, which is what
   `ehtle/stats.py` now does.
2. **A model that scores highly on `constrained-optimisation` has been tested four times, not
   once.** That is reliability evidence, not breadth evidence, and the write-up must not present
   four worlds as four independent confirmations.
3. **W10 and W11 are close enough that a discriminative claim about one should be checked against
   the other.** I have not removed either, and I am not going to add a thirteenth world to paper
   over it, because that would be a new untested artefact rather than a fix.
4. **I cannot resolve whether these boundaries are right.** A second reviewer should derive the
   families independently from the published contracts *before* reading this file. If they disagree
   with `FAMILIES`, they should be believed over it.
