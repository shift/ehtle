import json
import os
import signal
import subprocess
from pathlib import Path

from .common import canonical
from .engine import Episode
from .framing import condition_name
from .policies import choose


def strict_json(text):
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result

    def constant(value):
        raise ValueError('Non-finite JSON number')

    return json.loads(text, object_pairs_hook=object_pairs, parse_constant=constant)


def adapter_call(argv, view, timeout=30):
    """Invoke a TRUSTED adapter, shell=False. Filesystem/network are not restricted.

    This is a transport fixture, not containment. See ``ehtle.isolation`` for the bridge that
    keeps evaluator state and provider credentials away from the tested system.
    """
    if not isinstance(argv, list) or not argv or any(not isinstance(x, str) for x in argv):
        raise ValueError('Adapter command must be a nonempty JSON array of strings')
    if timeout <= 0:
        raise ValueError('Timeout must be positive')
    proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, start_new_session=True)
    try:
        stdout, _ = proc.communicate(canonical(view), timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.communicate()
        raise TimeoutError('Adapter exceeded per-call timeout') from None
    if proc.returncode:
        raise RuntimeError(f'Adapter exited with code {proc.returncode}')
    if len(stdout.encode()) > 262144:
        raise ValueError('Adapter output exceeds protocol limit')
    return strict_json(stdout)


def run_episode(world_id, variant, seed=0, policy=None, adapter=None, timeout=30, *,
                framing='ordinary', framing_timing='immediate', safety_gate=False, scenario=None,
                decider=None):
    """Run one episode. Exactly one decision source: a scripted policy, a trusted adapter
    process, or a callable decider such as the local model bridge."""
    sources = [source is not None for source in (policy, adapter, decider)]
    if sum(sources) != 1:
        raise ValueError('Specify exactly one of policy, adapter or decider')
    episode = Episode(world_id, variant, seed, framing=framing, framing_timing=framing_timing,
                      safety_gate=safety_gate, scenario=scenario)
    while not episode.done:
        view = episode.view()
        try:
            if policy:
                reply = choose(policy, view)
            elif adapter:
                reply = adapter_call(adapter, view, timeout)
            else:
                reply = decider(view)
        except (OSError, ValueError, RuntimeError, TimeoutError) as exc:
            episode.fail(type(exc).__name__, str(exc))
            break
        episode.step(reply)
    return episode.artifact()


def _framing_statistics(traces):
    from .stats import report as statistics
    return statistics(traces)


def _write(path, trace):
    (path / (condition_name(trace['config']) + '.json')).write_text(json.dumps(trace, indent=2) + '\n')


def run_framing_suite(out, seed=0, policy=None, adapter=None, timeout=30, scenario=None,
                     decider=None, run_record=None, subset=None):
    from .framing import conditions
    from .reporting import summarize, framing_contrasts, reversal_denominators, safeguard_denominators
    from .engine import replay
    path = Path(out)
    if path.exists() and any(path.iterdir()):
        raise ValueError('Use an empty output directory to preserve earlier runs')
    path.mkdir(parents=True, exist_ok=True)
    traces = []
    selected = list(conditions())
    if subset is not None:
        selected = [selected[i] for i in subset]
    for config in selected:
        trace = run_episode(**config, seed=seed, policy=policy, adapter=adapter, timeout=timeout,
                            scenario=scenario, decider=decider)
        replay(trace)
        _write(path, trace)
        traces.append(trace)
    summary = {
        **summarize(traces),
        'paired_framing_contrasts': framing_contrasts(traces),
        'reversal_denominators': reversal_denominators(traces),
        'safeguard_denominators': safeguard_denominators(traces),
        'statistics': _framing_statistics(traces),
        'kind': 'scripted_fixture_validation' if policy else 'model_run',
        'policy': policy,
        'run_record': run_record,
        'adapter_uses_fresh_process_per_decision': True,
        'condition_count': len(selected), 'scheduled_condition_count': 96,
        'subset_indices': list(subset) if subset is not None else None,
        'independent_worlds': 1, 'replay_verified': True,
        'extension': True, 'core_results_included': False,
    }
    (path / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary


def run_core_suite(out, worlds, variants, seeds=(0, 1, 2), policy=None, adapter=None,
                   timeout=30, scenario=None, scenarios=None, decider=None, run_record=None):
    """The matched quartet (optionally repeated) over the twelve original worlds."""
    from .reporting import summarize, core_contrasts
    from .stats import report as statistics
    from .engine import replay
    if sum(source is not None for source in (policy, adapter, decider)) != 1:
        raise ValueError('Specify exactly one of policy, adapter or decider')
    path = Path(out)
    if path.exists() and any(path.iterdir()):
        raise ValueError('Use an empty output directory to preserve earlier runs')
    path.mkdir(parents=True, exist_ok=True)
    traces = []
    for world in worlds:
        for variant in variants:
            for seed in seeds:
                extra = (scenarios or {}).get((world, variant))
                trace = run_episode(world, variant, seed, policy, adapter, timeout,
                                    scenario=extra if extra is not None else scenario,
                                    decider=decider)
                replay(trace)
                _write(path, trace)
                traces.append(trace)
    summary = {
        **summarize(traces),
        'core_contrasts': core_contrasts(traces),
        'statistics': statistics(traces),
        'kind': 'scripted_fixture_validation' if policy else 'model_run',
        'policy': policy, 'run_record': run_record, 'replay_verified': True,
        'worlds': list(worlds), 'variants': list(variants), 'seeds': list(seeds),
        'independent_worlds': len(set(worlds)),
        'core_results_only': True, 'framing_extension_included': False,
    }
    (path / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary
