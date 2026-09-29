"""Pre-registered bounded local-model smoke run.

Scope, fixed before the run and reported in the run record:

* Six core episodes: W01 and W09 in both the conflict and the control condition, plus W03 and W06
  conflict conditions. This covers a metric-defect world, a consent-scope world, a composition
  world and a deferred-effect world.
* Four W13 framing conditions, chosen by index from the fixed 96-condition ordering: the
  role-play-after-refusal pair with the safeguard off and on, and the same pair in the verified
  isolated control.

This is a smoke run of the instrument, not a research result. It is far too small for any claim
about the model, and its purpose is to show that the bridge, the isolation boundary, the ledger,
replay and the scorer all work together on a real model.

    python3 scripts/smoke_model.py --endpoint URL --model ID --out results/model-smoke-001
"""
import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ehtle.framing import condition_name, conditions
from ehtle.isolation import BridgeConfig, LocalModelBridge, RunLedger, containment_probe, run_record
from ehtle.runner import run_core_suite, run_framing_suite
from ehtle.worlds import VARIANTS

CORE_WORLDS = ('W01', 'W09')
CORE_VARIANTS = ('D-audit', 'C-audit')
# D-audit role-play after a real refusal with the safeguard off (10) and on (11), and the
# identical pair in the verified isolated control (58, 59). Fixed before the run.
FRAMING_SUBSET = (10, 11, 58, 59)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--max-tokens', type=int, default=160)
    parser.add_argument('--timeout', type=float, default=900)
    parser.add_argument('--retries', type=int, default=1)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--model-notes', default='')
    parser.add_argument('--enable-thinking', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    config = BridgeConfig(args.endpoint, args.model, temperature=args.temperature,
                          max_tokens=args.max_tokens, seed=args.seed, timeout=args.timeout,
                          retries=args.retries, enable_thinking=args.enable_thinking,
                          model_notes=args.model_notes)
    ledger = RunLedger()
    bridge = LocalModelBridge(config, ledger=ledger)
    preflight = bridge.preflight()
    print(json.dumps(preflight), flush=True)
    out = Path(args.out)
    if out.exists() and any(out.iterdir()):
        raise SystemExit('refusing to overwrite a previous run; use a new output directory')
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    core = run_core_suite(out / 'core', CORE_WORLDS, CORE_VARIANTS, (args.seed,),
                          decider=bridge.decide)
    framing = run_framing_suite(out / 'framing', args.seed, decider=bridge.decide,
                                subset=list(FRAMING_SUBSET))
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, dir='/tmp') as handle:
        handle.write('ehtle-smoke-containment-probe')
        containment = containment_probe((root,), handle.name)
    finished = datetime.now(timezone.utc).isoformat()
    record = run_record(config, ledger, started, finished, CORE_WORLDS, CORE_VARIANTS, (args.seed,),
                        'local_model_smoke')
    record['preflight'] = preflight
    record['containment'] = containment
    record['preregistered_scope'] = {
        'core_worlds': list(CORE_WORLDS), 'core_variants': list(CORE_VARIANTS),
        'core_seeds': [args.seed],
        'framing_condition_indices': list(FRAMING_SUBSET),
        'framing_condition_names': [{'index': i, 'name': condition_name(conditions()[i])}
                                    for i in FRAMING_SUBSET],
        'declared_purpose': ('Instrument smoke run. Too small for any claim about the model, its '
                             'capability, its alignment or any real-world outcome.'),
    }
    (out / 'core' / 'summary.json').write_text(json.dumps(core, indent=2) + '\n')
    (out / 'framing' / 'summary.json').write_text(json.dumps(framing, indent=2) + '\n')
    (out / 'run_record.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'core': core['overall'], 'framing': framing['overall'],
                      'coverage': ledger.counts(), 'contained': containment['contained']}, indent=2))


if __name__ == '__main__':
    main()
