from .w01 import Beneficiaries
from .w02 import ReplacementDividend
from .w03 import CommitteeBudget
from .w04 import CumulativeRisk
from .w05 import KeyControl
from .w06 import DeferredEffects
from .w07 import ReportingRecord
from .w08 import OperatorScope
from .w09 import Workforce
from .w10 import ImmersiveWork
from .w11 import ConsentInheritance
from .w12 import PostAutomationSupport
from .w13 import ActuationBoundary

CORE_WORLDS = ('W01', 'W02', 'W03', 'W04', 'W05', 'W06', 'W07', 'W08', 'W09', 'W10', 'W11', 'W12')
FRAMING_WORLDS = ('W13',)
WORLDS = CORE_WORLDS + FRAMING_WORLDS
REGISTRY = {c.world_id: c for c in (Beneficiaries, ReplacementDividend, CommitteeBudget, CumulativeRisk,
                                    KeyControl, DeferredEffects, ReportingRecord, OperatorScope, Workforce,
                                    ImmersiveWork, ConsentInheritance, PostAutomationSupport,
                                    ActuationBoundary)}
VARIANTS = ('D-audit', 'D-sample', 'C-audit', 'C-sample')


def make_world(world_id, variant, seed, scenario=None):
    if world_id not in REGISTRY or variant not in VARIANTS:
        raise ValueError('Unknown world or variant')
    if type(seed) is not int or isinstance(seed, bool):
        raise ValueError('Seed must be an integer')
    return REGISTRY[world_id](variant.startswith('D-'), seed, variant, scenario)
