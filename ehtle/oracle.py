"""Finite reference search for the declared plan spaces, under the same charter."""
from .engine import Episode
from .policies import action


def solve(world_id,variant,seed=0):
    template=Episode(world_id,variant,seed)
    choices=[]
    # Include no-action outcome; no-action never wins these useful-task fixtures.
    candidates=[None]+list(template.world.candidates())
    for candidate in candidates:
        e=Episode(world_id,variant,seed)
        if candidate:
            for target in e.inspection_targets():
                e.step(action('inspect',object_id=target))
            plan,params=candidate
            e.step(action('commit',plan_id=plan,params=params,authority_ref='grant_1'))
        if not e.done: e.step(action('stop'))
        result=e.score()
        choices.append({'plan':candidate,'ranking':e.world.ranking(e.state['world']),
                        'compliant':not result['violation_attempt'] and not result['executed_breach'],
                        'score':result})
    return {'candidate_count':len(choices),
            'unconstrained':max(choices,key=lambda x:x['ranking']),
            'admissible':max((x for x in choices if x['compliant']),key=lambda x:x['ranking'])}
