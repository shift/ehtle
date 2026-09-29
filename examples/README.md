# Example adapters

`baseline_adapter.py` is a **protocol fixture**, not a model. It runs the same scripted policy
library the verifier uses, so it exercises the adapter transport end to end without any inference.

```sh
python3 -m ehtle run --world W09 --variant D-audit \
    --adapter-argv examples/adapter-argv.json --out results/adapter-demo.json
python3 -m ehtle replay results/adapter-demo.json
```

A real adapter reads one JSON model view from stdin and writes one action object on stdout:

```json
{"tool": "inspect", "args": {"object_id": "plan_contract"}}
```

Its command is a JSON argv array, executed without a shell, and the process is restarted on every
decision. Duplicate JSON keys, non-finite numbers, unknown tools, wrong shapes and output over
256 KiB are all recorded as failures with terminal settlement.

**The adapter process is not sandboxed.** It inherits ordinary filesystem and network permissions
and can read this repository, including the answer keys. For an untrusted coding agent use
`ehtle.isolation.sandbox`, which masks the project root, clears the environment, makes the
filesystem read-only, unshares the network and applies resource limits. For a local model use
`ehtle.isolation.bridge`, which keeps the model call inside the evaluator's process and hands the
model an allowlist projection of the view.
