import argparse
import json
from pathlib import Path
from .engine import replay
from .oracle import solve
from .policies import ALL_POLICIES
from .framing import FRAMINGS, TIMINGS
from .runner import run_episode, run_framing_suite
from .worlds import REGISTRY, VARIANTS

def main():
    p=argparse.ArgumentParser(description='EHTLE stateful starter v0.5; fictional world effects.')
    sub=p.add_subparsers(dest='cmd',required=True)
    verification=sub.add_parser('verify'); verification.add_argument('--out',default='results/verification')
    run=sub.add_parser('run'); run.add_argument('--world',choices=REGISTRY,required=True)
    run.add_argument('--variant',choices=VARIANTS,required=True); run.add_argument('--seed',type=int,default=0)
    group=run.add_mutually_exclusive_group(required=True)
    group.add_argument('--policy',choices=ALL_POLICIES)
    group.add_argument('--adapter-argv',help='JSON file containing a trusted adapter argv array')
    run.add_argument('--timeout',type=float,default=30); run.add_argument('--out',required=True)
    run.add_argument('--framing',choices=FRAMINGS,default='ordinary')
    run.add_argument('--framing-timing',choices=TIMINGS,default='immediate')
    run.add_argument('--safety-gate',action='store_true')
    suite=sub.add_parser('framing-suite')
    suite_group=suite.add_mutually_exclusive_group(required=True)
    suite_group.add_argument('--policy',choices=ALL_POLICIES)
    suite_group.add_argument('--adapter-argv',help='JSON file containing a trusted adapter argv array')
    suite.add_argument('--seed',type=int,default=0)
    suite.add_argument('--timeout',type=float,default=30)
    suite.add_argument('--out',required=True)
    rep=sub.add_parser('replay'); rep.add_argument('trace')
    oracle=sub.add_parser('oracle'); oracle.add_argument('--world',choices=REGISTRY,required=True)
    oracle.add_argument('--variant',choices=VARIANTS,required=True); oracle.add_argument('--seed',type=int,default=0)
    args=p.parse_args()
    if args.cmd=='verify':
        from .verify import verify
        verify(args.out)
    elif args.cmd=='run':
        argv=json.loads(Path(args.adapter_argv).read_text()) if args.adapter_argv else None
        trace=run_episode(args.world,args.variant,args.seed,args.policy,argv,args.timeout,
                          framing=args.framing,framing_timing=args.framing_timing,safety_gate=args.safety_gate)
        path=Path(args.out); path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(trace,indent=2)+'\n'); print(json.dumps(trace['score'],indent=2))
    elif args.cmd=='framing-suite':
        argv=json.loads(Path(args.adapter_argv).read_text()) if args.adapter_argv else None
        summary=run_framing_suite(args.out,args.seed,args.policy,argv,args.timeout)
        print(json.dumps(summary['overall'],indent=2))
    elif args.cmd=='replay': print(json.dumps(replay(json.loads(Path(args.trace).read_text())),indent=2))
    else: print(json.dumps(solve(args.world,args.variant,args.seed),indent=2))
if __name__=='__main__': main()
