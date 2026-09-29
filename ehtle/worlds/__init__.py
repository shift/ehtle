from .w01 import Beneficiaries
from .w06 import DeferredEffects
from .w09 import Workforce
from .w13 import ActuationBoundary

REGISTRY={c.world_id:c for c in (Beneficiaries,DeferredEffects,Workforce,ActuationBoundary)}
CORE_WORLDS=('W01','W06','W09')
VARIANTS=('D-audit','D-sample','C-audit','C-sample')

def make_world(world_id,variant,seed):
    if world_id not in REGISTRY or variant not in VARIANTS:
        raise ValueError('Unknown world or variant')
    if type(seed) is not int: raise ValueError('Seed must be an integer')
    return REGISTRY[world_id](variant.startswith('D-'),seed)
