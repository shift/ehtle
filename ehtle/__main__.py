import argparse
import json
from pathlib import Path

from .engine import replay
from .oracle import solve
from .policies import ALL_POLICIES
from .framing import FRAMINGS, TIMINGS
from .isolation import BridgeConfig, LocalModelBridge, RunLedger, containment_probe, run_record
from .runner import run_episode, run_framing_suite, run_core_suite
from .worlds import CORE_WORLDS, FRAMING_WORLDS, REGISTRY, VARIANTS


def main():
    p = argparse.ArgumentParser(description='EHTLE stateful benchmark v0.6; fictional world effects only.')
    sub = p.add_subparsers(dest='cmd', required=True)
    verification = sub.add_parser('verify')
    verification.add_argument('--out', default='results/verification')
    run = sub.add_parser('run')
    run.add_argument('--world', choices=sorted(REGISTRY), required=True)
    run.add_argument('--variant', choices=VARIANTS, required=True)
    run.add_argument('--seed', type=int, default=0)
    group = run.add_mutually_exclusive_group(required=True)
    group.add_argument('--policy', choices=ALL_POLICIES)
    group.add_argument('--adapter-argv', help='JSON file containing a trusted adapter argv array')
    run.add_argument('--timeout', type=float, default=30)
    run.add_argument('--out', required=True)
    run.add_argument('--framing', choices=FRAMINGS, default='ordinary')
    run.add_argument('--framing-timing', choices=TIMINGS, default='immediate')
    run.add_argument('--safety-gate', action='store_true')
    run.add_argument('--scenario', help='JSON object of scenario parameters for the episode')
    suite = sub.add_parser('framing-suite')
    suite_group = suite.add_mutually_exclusive_group(required=True)
    suite_group.add_argument('--policy', choices=ALL_POLICIES)
    suite_group.add_argument('--adapter-argv')
    suite.add_argument('--seed', type=int, default=0)
    suite.add_argument('--timeout', type=float, default=30)
    suite.add_argument('--out', required=True)
    core = sub.add_parser('core-suite')
    core_group = core.add_mutually_exclusive_group(required=True)
    core_group.add_argument('--policy', choices=ALL_POLICIES)
    core_group.add_argument('--adapter-argv')
    core.add_argument('--worlds', nargs='*', default=list(CORE_WORLDS), choices=sorted(REGISTRY))
    core.add_argument('--seeds', nargs='*', type=int, default=[0, 1, 2])
    core.add_argument('--timeout', type=float, default=30)
    core.add_argument('--out', required=True)
    rep = sub.add_parser('replay')
    rep.add_argument('trace')
    oracle = sub.add_parser('oracle')
    oracle.add_argument('--world', choices=sorted(REGISTRY), required=True)
    oracle.add_argument('--variant', choices=VARIANTS, required=True)
    oracle.add_argument('--seed', type=int, default=0)
    oracle.add_argument('--scenario')
    model = sub.add_parser('model-run', help='bounded evaluation through the trusted local bridge')
    model.add_argument('--endpoint', required=True)
    model.add_argument('--model', required=True)
    model.add_argument('--temperature', type=float, default=0.0)
    model.add_argument('--top-p', type=float, default=1.0)
    model.add_argument('--max-tokens', type=int, default=512)
    model.add_argument('--model-seed', type=int, default=0)
    model.add_argument('--retries', type=int, default=1)
    model.add_argument('--timeout', type=float, default=90)
    model.add_argument('--credential-env', default=None)
    model.add_argument('--enable-thinking', action='store_true')
    model.add_argument('--model-notes', default='')
    model.add_argument('--suite', choices=('core', 'framing'), default='core')
    model.add_argument('--worlds', nargs='*', default=list(CORE_WORLDS), choices=sorted(REGISTRY))
    model.add_argument('--seeds', nargs='*', type=int, default=[0])
    model.add_argument('--out', required=True)
    model.add_argument('--framing-subset', nargs='*', type=int, default=None,
                       help='preregistered indices into the 96 framing conditions')
    model.add_argument('--containment-report')
    stats = sub.add_parser('stats', help='world-clustered statistics over a results directory')
    stats.add_argument('directory')
    stats.add_argument('--out')
    stats.add_argument('--seed', type=int, default=0)
    isolation = sub.add_parser('isolation-check', help='publish an adversarial containment probe')
    isolation.add_argument('--out')
    probe = sub.add_parser('probe')
    probe.add_argument('--list', action='store_true')
    probe.add_argument('--id')
    probe.add_argument('--submit', help='JSON file with a probe id and submitted answer object')
    args = p.parse_args()
    try:
        if args.cmd == 'verify':
            from .verify import verify
            verify(args.out)
        elif args.cmd == 'run':
            argv = json.loads(Path(args.adapter_argv).read_text()) if args.adapter_argv else None
            scenario = json.loads(args.scenario) if args.scenario else None
            trace = run_episode(args.world, args.variant, args.seed, args.policy, argv, args.timeout,
                                framing=args.framing, framing_timing=args.framing_timing,
                                safety_gate=args.safety_gate, scenario=scenario)
            path = Path(args.out)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(trace, indent=2) + '\n')
            print(json.dumps(trace['score'], indent=2))
        elif args.cmd == 'framing-suite':
            argv = json.loads(Path(args.adapter_argv).read_text()) if args.adapter_argv else None
            summary = run_framing_suite(args.out, args.seed, args.policy, argv, args.timeout)
            print(json.dumps(summary['overall'], indent=2))
        elif args.cmd == 'core-suite':
            argv = json.loads(Path(args.adapter_argv).read_text()) if args.adapter_argv else None
            summary = run_core_suite(args.out, args.worlds, VARIANTS, args.seeds, args.policy, argv, args.timeout)
            print(json.dumps(summary['overall'], indent=2))
        elif args.cmd == 'replay':
            print(json.dumps(replay(json.loads(Path(args.trace).read_text())), indent=2))
        elif args.cmd == 'model-run':
            from datetime import datetime, timezone
            out_path = Path(args.out)
            config = BridgeConfig(args.endpoint, args.model, temperature=args.temperature,
                                  top_p=args.top_p, max_tokens=args.max_tokens,
                                  seed=args.model_seed, timeout=args.timeout,
                                  retries=args.retries, credential_env=args.credential_env,
                                  enable_thinking=args.enable_thinking,
                                  model_notes=args.model_notes)
            ledger = RunLedger()
            bridge = LocalModelBridge(config, ledger=ledger)
            started = datetime.now(timezone.utc).isoformat()
            worlds = FRAMING_WORLDS if args.suite == 'framing' else tuple(args.worlds)
            if args.suite == 'framing':
                summary = run_framing_suite(args.out, args.seeds[0], decider=bridge.decide,
                                            subset=args.framing_subset)
            else:
                summary = run_core_suite(args.out, worlds, VARIANTS, tuple(args.seeds),
                                         decider=bridge.decide)
            record = run_record(config, ledger, started,
                                datetime.now(timezone.utc).isoformat(), worlds, VARIANTS,
                                args.seeds, f'local_model_{args.suite}')
            if args.containment_report:
                import tempfile
                root = Path(__file__).resolve().parents[1]
                with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, dir='/tmp') as fh:
                    fh.write('ehtle-containment-probe')
                    record['containment'] = containment_probe((root,), fh.name)
            summary['run_record'] = record
            (out_path / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
            (out_path / 'run_record.json').write_text(json.dumps(record, indent=2) + '\n')
            print(json.dumps(summary['overall'], indent=2))
        elif args.cmd == 'stats':
            from .stats import report as statistics
            directory = Path(args.directory)
            traces = [json.loads(p.read_text()) for p in sorted(directory.glob('*.json'))
                      if p.name not in ('summary.json', 'run_record.json', 'probes.json')
                      and isinstance(json.loads(p.read_text()), dict)
                      and 'score' in json.loads(p.read_text())]
            if not traces:
                raise ValueError(f'no episode traces found in {directory}')
            result = statistics(traces, seed=args.seed)
            text = json.dumps(result, indent=2)
            if args.out:
                Path(args.out).write_text(text + '\n')
            print(text)
        elif args.cmd == 'isolation-check':
            import tempfile
            root = Path(__file__).resolve().parents[1]
            with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, dir='/tmp') as fh:
                fh.write('ehtle-containment-probe')
                observation = containment_probe((root,), fh.name)
            print(json.dumps(observation, indent=2))
            if args.out:
                Path(args.out).write_text(json.dumps(observation, indent=2) + '\n')
        elif args.cmd == 'probe':
            from .probes import PROBES, probe_context, score_probe
            if args.list or not args.id:
                print(json.dumps([{'id': x['id'], 'world': x['world'], 'variant': x['variant'],
                                   'family': x['family'], 'question': x['question']} for x in PROBES],
                                 indent=2))
            elif args.submit:
                payload = json.loads(Path(args.submit).read_text())
                print(json.dumps(score_probe(payload['id'], payload['answer']), indent=2))
            else:
                found = next(x for x in PROBES if x['id'] == args.id)
                print(json.dumps(probe_context(found), indent=2))
        else:
            scenario = json.loads(args.scenario) if args.scenario else None
            print(json.dumps(solve(args.world, args.variant, args.seed, scenario), indent=2))
    except (ValueError, OSError, RuntimeError, TimeoutError) as exc:
        p.exit(2, f'error: {type(exc).__name__}: {exc}\n')


if __name__ == '__main__':
    main()
