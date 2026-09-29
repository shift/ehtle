"""Real process isolation and a trusted local inference bridge.

Importing this package does not require bubblewrap. Commands that need a sandbox raise
:class:`IsolationUnavailable` when ``bwrap`` is absent, so containment is never silently skipped.
"""
from .bridge import (ALLOWED_VIEW_KEYS, BridgeConfig, BridgeError, LocalModelBridge, RunLedger,
                     project, run_record)
from .sandbox import (IsolationUnavailable, SandboxSpec, bubblewrap_available, containment_probe,
                      run_sandboxed)

__all__ = ['ALLOWED_VIEW_KEYS', 'BridgeConfig', 'BridgeError', 'LocalModelBridge', 'RunLedger',
           'project', 'run_record', 'IsolationUnavailable', 'SandboxSpec',
           'bubblewrap_available', 'containment_probe', 'run_sandboxed']
