"""Protocol fixture, not a language model. Consumes only the supplied view."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ehtle.policies import choose, ALL_POLICIES
p=argparse.ArgumentParser(); p.add_argument('--policy',choices=ALL_POLICIES,default='constrained')
args=p.parse_args()
print(json.dumps(choose(args.policy,json.load(sys.stdin))))
