"""Protocol fixture, not a language model. Consumes only the supplied view.

This process is TRUSTED and is not sandboxed: it has ordinary filesystem and network permissions.
Use `ehtle.isolation.sandbox` for an untrusted coding agent, or
`scripts/bridge_transport_check.py` for a local model.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ehtle.policies import ALL_POLICIES, choose  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument('--policy', choices=ALL_POLICIES, default='constrained')
args = parser.parse_args()
print(json.dumps(choose(args.policy, json.load(sys.stdin))))
