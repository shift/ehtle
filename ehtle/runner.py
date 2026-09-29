import json
import os
import signal
import subprocess
from .engine import Episode
from .policies import choose
from .common import canonical

def strict_json(text):
    def object_pairs(pairs):
        result={}
        for key,value in pairs:
            if key in result: raise ValueError('Duplicate JSON key')
            result[key]=value
        return result
    def constant(value): raise ValueError('Non-finite JSON number')
    return json.loads(text,object_pairs_hook=object_pairs,parse_constant=constant)

def adapter_call(argv,view,timeout=30):
    """Invoke a TRUSTED adapter, shell=False. Filesystem/network are not restricted."""
    if not isinstance(argv,list) or not argv or any(not isinstance(x,str) for x in argv):
        raise ValueError('Adapter command must be a nonempty JSON array of strings')
    if timeout<=0: raise ValueError('Timeout must be positive')
    proc=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                          text=True,start_new_session=True)
    try:
        stdout,_=proc.communicate(canonical(view),timeout=timeout)
    except subprocess.TimeoutExpired:
        try: os.killpg(proc.pid,signal.SIGKILL)
        except ProcessLookupError: pass
        proc.communicate()
        raise TimeoutError('Adapter exceeded per-call timeout') from None
    if proc.returncode: raise RuntimeError(f'Adapter exited with code {proc.returncode}')
    if len(stdout.encode())>262144: raise ValueError('Adapter output exceeds protocol limit')
    return strict_json(stdout)

def run_episode(world_id,variant,seed=0,policy=None,adapter=None,timeout=30,*,
                framing='ordinary',framing_timing='immediate',safety_gate=False):
    if (policy is None)==(adapter is None): raise ValueError('Specify one policy or adapter')
    e=Episode(world_id,variant,seed,framing=framing,framing_timing=framing_timing,safety_gate=safety_gate)
    while not e.done:
        try: reply=choose(policy,e.view()) if policy else adapter_call(adapter,e.view(),timeout)
        except (OSError,ValueError,RuntimeError,TimeoutError) as exc:
            e.fail(type(exc).__name__,str(exc)); break
        e.step(reply)
    return e.artifact()

def run_framing_suite(out,seed=0,policy=None,adapter=None,timeout=30):
    from pathlib import Path
    from .framing import conditions, condition_name
    from .reporting import summarize, framing_contrasts
    from .engine import replay
    path=Path(out)
    if path.exists() and any(path.iterdir()): raise ValueError('Use an empty output directory to preserve earlier runs')
    path.mkdir(parents=True,exist_ok=True)
    traces=[]
    for config in conditions():
        trace=run_episode(**config,seed=seed,policy=policy,adapter=adapter,timeout=timeout)
        replay(trace)
        (path/(condition_name(config)+'.json')).write_text(json.dumps(trace,indent=2)+'\n')
        traces.append(trace)
    summary={**summarize(traces),'paired_framing_contrasts':framing_contrasts(traces),
             'kind':'scripted_fixture_validation' if policy else 'adapter_run',
             'policy':policy,'adapter_uses_fresh_process_per_decision':True,
             'condition_count':96,'independent_worlds':1,'replay_verified':True}
    (path/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary
