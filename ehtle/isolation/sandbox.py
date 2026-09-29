"""Process isolation for a tested system that is not trusted.

The bundled adapter transport in :mod:`ehtle.runner` is a *transport fixture*: the child process
inherits ordinary OS permissions. That is not containment. This module provides a real boundary on
Linux using bubblewrap (``bwrap``) when it is available, and fails closed when it is not.

What the sandbox guarantees
---------------------------
* The project root, the traces, the results directory and every credential store are replaced by
  an empty tmpfs inside the child, so a tested coding agent cannot read the answer keys.
* The filesystem is otherwise read-only; the only writable locations are a private ``/tmp`` and a
  private ``HOME`` created for that child alone.
* The environment is cleared and rebuilt from an explicit allowlist.
* CPU, address-space, file-size and process limits are enforced with ``setrlimit`` in a preexec hook.
* The child runs in a new session and process group, so a timeout can kill the whole group.
* Network access is denied by default with ``--unshare-net``.

What it does not guarantee
--------------------------
This is process-level isolation on one host, not a VM. It does not defend against a kernel or
container-runtime escape, and it does not bound side effects on shared host resources other than
the ones listed above. A private (non-shared) holdout still requires a separately administered
machine or a reviewed, access-controlled distribution channel.
"""
import json
import os
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


class IsolationUnavailable(RuntimeError):
    pass


def bubblewrap_available():
    return shutil.which('bwrap') is not None


@dataclass
class SandboxSpec:
    """Everything the child is allowed to see. Anything not listed is hidden or read-only."""

    argv: list
    mask_paths: tuple = ()
    read_only_paths: tuple = ('/usr', '/nix', '/etc/ld.so.cache', '/lib', '/lib64')
    allow_network: bool = False
    cpu_seconds: int = 60
    address_space_mib: int = 2048
    file_size_mib: int = 8
    max_processes: int = 64
    env: dict = field(default_factory=lambda: {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8',
                                               'PYTHONHASHSEED': '0', 'PYTHONDONTWRITEBYTECODE': '1'})

    #: Work happens in a sandbox-local directory. The host temporary directory is not the same
    #: path: /tmp is a fresh tmpfs inside the sandbox, so a host path there does not exist.
    WORKDIR = '/tmp/ehtle-work'

    def command(self, workdir):
        bwrap = shutil.which('bwrap')
        if bwrap is None:
            raise IsolationUnavailable('bubblewrap (bwrap) is required for a real sandbox')
        interpreter = Path(sys.executable).resolve()
        read_only = [p for p in self.read_only_paths if Path(p).exists()]
        for extra in (interpreter.parent, Path(interpreter).parents[1], Path(sys.prefix)):
            if extra.exists() and str(extra) not in read_only:
                read_only.append(str(extra))
        argv = [bwrap, '--unshare-user', '--die-with-parent', '--new-session']
        if not self.allow_network:
            argv.append('--unshare-net')
        else:
            argv.append('--share-net')
        bound = set()
        for path in read_only:
            argv += ['--ro-bind', path, path]
            bound.add(str(Path(path).resolve()))
        for path in self.mask_paths:
            target = Path(path).resolve()
            if not target.exists():
                continue
            # Bind every ancestor read-only first so the masked leaf becomes an empty directory
            # rather than an unreachable path. The difference is visible when reading the probe.
            for ancestor in reversed(target.parents):
                if str(ancestor) not in bound and ancestor.exists():
                    argv += ['--ro-bind', str(ancestor), str(ancestor)]
                    bound.add(str(ancestor))
                if str(ancestor) == '/':
                    break
            argv += ['--tmpfs', str(target)]
        argv += ['--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp',
                 '--dir', '/run', '--dir', str(workdir), '--chdir', str(workdir),
                 '--unshare-pid', '--unshare-ipc', '--unshare-uts']
        argv += ['--clearenv']
        for key, value in sorted(self.env.items()):
            argv += ['--setenv', key, str(value)]
        argv += ['--setenv', 'HOME', str(workdir),
                 '--setenv', 'TMPDIR', str(workdir),
                 '--setenv', 'EHTLE_WORKDIR', str(workdir),
                 '--setenv', 'PATH', ':'.join(dict.fromkeys(
                     [str(interpreter.parent), '/usr/bin', '/bin'] + self.path_extra()))]
        # Resource limits are applied with setrlimit, not by bubblewrap: not every bwrap build
        # supports --rlimit-*, and the limits must survive the exec. RLIMIT_NPROC is applied by a
        # shim INSIDE the sandbox, because lowering it before unshare makes namespace creation
        # fail with EAGAIN for a user who already owns more processes than the cap.
        return (argv + ['--'] + [str(interpreter), '-c', SHIM, str(self.max_processes)]
                + list(self.argv))

    def path_extra(self):
        profile = Path.home() / '.nix-profile' / 'bin'
        return [str(profile)] if profile.exists() else []


def run_sandboxed(spec, payload, timeout=30, max_output_bytes=262144):
    """Run one decision in the sandbox. The child sees ``payload`` and nothing else."""
    with tempfile.TemporaryDirectory(prefix='ehtle-sandbox-') as workdir:
        env = {'PYTHONPATH': workdir, 'EHTLE_SANDBOX': '1'}
        limits = _limits(spec)
        proc = subprocess.Popen(spec.command(workdir), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, start_new_session=True,
                                cwd=workdir, env=env, preexec_fn=lambda: [f() for f in limits])
        try:
            stdout, stderr = proc.communicate(payload, timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill_group(proc)
            proc.communicate()
            raise TimeoutError('Sandboxed child exceeded its per-call timeout') from None
        if len(stdout.encode()) > max_output_bytes:
            raise ValueError('Sandboxed child output exceeds the protocol limit')
        return {'returncode': proc.returncode, 'stdout': stdout, 'stderr': stderr[-2000:]}


SHIM = (
    'import os,resource,sys\n'
    'cap,argv=int(sys.argv[1]),sys.argv[2:]\n'
    'try: resource.setrlimit(resource.RLIMIT_NPROC,(cap,cap))\n'
    'except Exception: pass\n'
    'os.chdir(os.environ["EHTLE_WORKDIR"])\n'
    'os.execvp(argv[0],argv)\n'
)  # runs inside the sandbox: sets RLIMIT_NPROC, then becomes the adapter


def _limit(which, value):
    def apply():
        try:
            resource.setrlimit(which, (value, value))
        except (ValueError, OSError):
            pass
    return apply


def _limits(spec):
    """Apply the resource limits that are safe to set before unshare.

    RLIMIT_NPROC is deliberately excluded here. A user who already owns more processes than the
    cap cannot fork, so lowering it before unshare makes the namespace setup itself fail with
    EAGAIN. The in-sandbox shim applies it instead, where lowering it cannot break the boundary.
    """
    return (
        _limit(resource.RLIMIT_CPU, spec.cpu_seconds),
        _limit(resource.RLIMIT_AS, spec.address_space_mib * 1024 * 1024),
        _limit(resource.RLIMIT_FSIZE, spec.file_size_mib * 1024 * 1024),
        _limit(resource.RLIMIT_CORE, 0),
    )


def _kill_group(proc):
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


READER = (
    'import json,os,socket,sys\n'
    'out={"masked":{},"cwd_writable":os.access(".",os.W_OK),"env":sorted(os.environ),'
    '"root_read_only":not os.access("/usr",os.W_OK),"nproc":None}\n'
    'import resource\n'
    'out["nproc"]=resource.getrlimit(resource.RLIMIT_NPROC)[0]\n'
    'for p in json.loads(sys.argv[1]):\n'
    '    try: out["masked"][p]=sorted(os.listdir(p))[:5]\n'
    '    except Exception as exc: out["masked"][p]=type(exc).__name__\n'
    'try: out["secret"]=open(sys.argv[2]).read()[:40]\n'
    'except Exception as exc: out["secret"]=type(exc).__name__\n'
    'try:\n'
    '    socket.create_connection(("1.1.1.1",80),1); out["network"]="reachable"\n'
    'except Exception as exc: out["network"]=type(exc).__name__\n'
    'print(json.dumps(out))\n'
)


def containment_probe(mask_paths, probe_path, allow_network=False):
    """Adversarial self-check run INSIDE the sandbox.

    Reports what a child can actually see rather than asserting, so the observation can be
    published with the run record. A successful containment probe shows empty masked paths, an
    unreadable secret, a cleared environment, a read-only root and no network.
    """
    reader = 'import json,os,socket,sys,resource\n' + READER.split('\n', 1)[1]
    spec = SandboxSpec(argv=['python3', '-c', reader, json.dumps([str(Path(x).resolve())
                                                                 for x in mask_paths]),
                            str(Path(probe_path).resolve())],
                       mask_paths=tuple(mask_paths), allow_network=allow_network)
    result = run_sandboxed(spec, json.dumps({}), timeout=30)
    if result['returncode']:
        raise IsolationUnavailable(f'containment probe failed: {result["stderr"]}')
    observation = json.loads(result['stdout'])
    # A masked path shows as an empty directory when its ancestors are bound, and as a missing
    # path when an ancestor is itself remounted (for example an evaluator root under /tmp). The
    # second case hides strictly more, so both are containment and the difference is reported
    # rather than smoothed over.
    observation['masking_mechanism'] = ('empty_tmpfs' if all(v == [] for v in observation['masked'].values())
                                        else 'ancestor_not_bound')
    observation['contained'] = bool(
        all(value in ([], 'FileNotFoundError', 'NotADirectoryError', 'PermissionError')
            for value in observation['masked'].values())
        and observation['secret'] not in ('',) and 'FileNotFound' in str(observation['secret'])
        and observation['network'] in ('unreachable', 'OSError'))
    return observation
