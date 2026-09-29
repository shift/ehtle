# Instructions for local agents

Read `HANDOFF.md`, `docs/IMPLEMENTATION.md` and your assigned file under `agents/` before editing. The repository is initialised and the verified baseline is committed. The v0.6 workstreams were executed sequentially in one working tree, because no delegation mechanism was available; there is no independent review behind any key in this package, and nothing should be read as reviewed.

## Working rules

- Use the ownership table in `HANDOFF.md`. Do not edit another workstream's files without coordinating with its owner. Schema/engine changes belong to the core owner; registry and release integration belong to the coordinator.
- Run `python3 -m ehtle verify` before claiming the initial snapshot is healthy. After changes, run relevant semantic checks and the shared acceptance command once integration is ready.
- Preserve distinctions between proposals, requests, denied requests, applied effects, future effects and reports. Stop, failure and refusal cannot erase an earlier commitment.
- Keep scenario consequences in the fictional simulator. Do not add real-world harm mechanisms or connect fake world actions to actual people/services.
- Keep evaluator state outside the model-facing view. A trusted local adapter subprocess is not an isolation boundary. Use `ehtle.isolation.sandbox` for an untrusted coding agent and `ehtle.isolation.bridge` for a local model, and publish the containment observation rather than asserting containment.
- Public task rules must justify the keys. A model claiming something is safe is not scoring evidence. Use traces and independently specified expected outcomes.
- Give each new world a paired causal control, an explicit success predicate, all required information within budget, and honest handling of infeasibility.
- Do not change expected outcomes solely to make a test pass. Explain any correction in the review record and version affected datasets/traces.
- New hypotheses and score changes must be declared before evaluation. Store all runs, including failures; label scripted fixtures and real-model results distinctly.
- Never embed API keys, private holdout contents or unredacted provider credentials in commits, traces, prompts or release archives. A credential lives in the evaluator process environment and nowhere else.
- Preserve every model attempt, including provider errors and retries. A dropped attempt is dropped evidence, not a nuisance.
- State plainly what evidence is. A scripted fixture is not a model result, a transport check is not an episode, and a smoke run of a handful of episodes is not a rate.

## Compatibility

Protocol and trace version 0.6 describe this implementation. `ehtle/_v05/` is the frozen 0.5 engine and replays 0.5 traces byte-identically; the frozen 0.4 package in `compat/` preserves 0.4 replay semantics. `replay()` dispatches on the trace version and rejects anything it cannot reproduce. Expanding state shape or semantics can invalidate state hashes even when aggregate scores stay similar. Propose a versioned transition and preserve frozen snapshots. A hash chain is a consistency check, not proof against a privileged author replacing an entire trace.

For W13 changes, also read `docs/FRAMING_CASES.md`. Preserve the separation between actual agent refusals and supplied history, model violations and safeguard interventions, and one underlying world and its 96 related conditions. Do not count a missing follow-up or unchallenged safeguard as a demonstrated success. Keep the extension results separate from the core results.
