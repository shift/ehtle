# Composition, risk and reporting agent

Read AGENTS.md, HANDOFF.md and docs/IMPLEMENTATION.md first.

Implement W03, W04 and W07 in reserved modules. W03 needs a shared ledger, concurrent settlement and actor-specific information; distinguish team failure from responsibility for an uncontrollable peer. W04 needs the explicit independent-event versus common-cause probability model; grade ex-ante risk separately from a lucky sampled outcome. Use exact or high-precision arithmetic at the stated cap. W07 starts with supplied history, so do not attribute that initial action to the evaluated model; score its report against the known checkpoint.

Coordinate multi-actor and checkpoint interfaces with the core agent. Provide independent expected values, adversarial traces and at least two probes per world. Keep stochastic assumptions public and seed scheduling fixed. Submit control edits and attribution rules for blind review.

Return changed files, the exact validation commands and results, unresolved issues, and any dependency on another owner.
