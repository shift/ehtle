# Core engine and adapter agent

Read AGENTS.md, HANDOFF.md and docs/IMPLEMENTATION.md first.

Own engine/common/runner/CLI/base-world interfaces, new adapters/isolation code and core tests. Generalise the current single-commit engine to scoped commitments, actor identities, revocation and delegation without losing attempted/denied/applied distinctions. Add review responses and exogenous events required by world authors. Track historical breaches in worlds that can later recover.

Coordinate interfaces with world authors before editing. Add explicit cancellation/inherited-grant semantics rather than guessing them. Keep all pending effects settling after stop, timeout and malformed output. Propose a new trace version for changes to state shape or semantics and document replay compatibility.

Implement a restricted inference bridge for the chosen local/hosted provider, with evaluator keys inaccessible to the tested agent. The existing trusted subprocess adapter is only a transport fixture, not containment. Bound process resources and preserve model/configuration/budget metadata. Deliver adversarial access checks, error/timeout traces and tested run commands.

Return changed files, the exact validation commands and results, unresolved issues, and any dependency on another owner.
