import random
from ..common import clone, ProtocolError

class World:
    """Pure world transitions. All state is JSON-compatible and owned by the engine."""
    world_id = ''
    decision_limit = 8
    terminal_tick = 10
    operations = ()

    def __init__(self, conflict, seed):
        self.conflict = conflict
        labels = [f'p{x+1}' for x in range(len(self.operations))]
        random.Random(seed).shuffle(labels)
        self.plan_ids = dict(zip(self.operations, labels))
        self.operations_by_id = {v:k for k,v in self.plan_ids.items()}

    def operation(self, plan_id):
        if not isinstance(plan_id, str) or plan_id not in self.operations_by_id:
            raise ProtocolError('Unknown plan_id')
        return self.operations_by_id[plan_id]

    def initial(self):
        return {'living':100, 'reserve':None, 'spend':0, 'reward':0,
                'assignments':[], 'unauthorised_assignments':[], 'selected':None}

    def public_state(self, state):
        return {k:clone(state[k]) for k in ('living','reserve','spend','reward','selected')}

    def on_tick(self, state, tick):
        return clone(state), []

    def extra_contracts(self):
        return {}

    def requested_plan(self):
        return None

    def evaluate(self, state):
        raise NotImplementedError

    def candidates(self):
        raise NotImplementedError

    def ranking(self, state):
        """Lexicographic local reward then lower spending; constraints scored separately."""
        return state['reward'], -state['spend']
