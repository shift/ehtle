"""Build a reproducible source/results ZIP after running `python3 -m ehtle verify`.

The archive carries source, documentation, the frozen compatibility archives and the verification
fixtures. It does not carry ad-hoc local model runs, which contain prompts and model output and
are published separately. The builder refuses to write inside the source tree and never overwrites
a manifest it did not generate.
"""
import argparse
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
# The licence files are listed explicitly because ROOT_FILES is an allowlist. An unlicensed
# release is a real failure mode and the archive must never be published without them.
ROOT_FILES = {'README.md', 'HANDOFF.md', 'AGENTS.md', 'pyproject.toml', '.gitignore',
              'LICENSE', 'LICENSE-DATA', 'NOTICE'}
DIRECTORIES = {'ehtle', 'tests', 'examples', 'agents', 'docs', 'compat', 'scripts', 'results',
                'review'}

REQUIRED_IN_ARCHIVE = ('LICENSE', 'LICENSE-DATA', 'NOTICE')
# .jsonl carries the per-attempt model ledger; excluding it would drop the evidence a run
# exists to produce.
SUFFIXES = {'.py', '.md', '.json', '.jsonl', '.toml', '.zip', '.sha256'}
# Results that belong in a public release. Everything else under results/ is a local run.
PUBLISHED_RESULTS = {'verification', 'model-smoke-001', 'model-core-w09-001',
                   'model-framing-smoke-001', 'model-framing-control-001', 'model-framing-control-002',
                   'model-probes-001', 'model-budget-check-001', 'model-spark-001',
                   'model-spark-core-001', 'model-spark-core-v2', 'model-spark-core-seeds12',
                   'model-spark-framing-001', 'model-spark-probes-001',
                   'model-armb-seed0-001', 'model-armb-seeds12', 'model-4b-screen-001',
                   'model-4b-core-seed0', 'model-4b-core-seeds12',
                   'model-4b-probes', 'model-4b-framing',
                   'model-4b-armb-seed0', 'model-4b-armb-seeds12',
                   'model-4b-v07b-screen', 'model-4b-v07-pilot',
                   'bridge-transport-check.json'}
FIXED_TIMESTAMP = (2026, 9, 29, 0, 0, 0)


def published(path):
    relative = path.relative_to(ROOT)
    if str(relative) in ROOT_FILES:
        return True
    if relative.parts[0] not in DIRECTORIES or path.suffix not in SUFFIXES:
        return False
    if relative.parts[0] == 'results':
        return relative.parts[1] in PUBLISHED_RESULTS if len(relative.parts) > 1 else False
    return True


def build(output, name='EHTLE-agent-handoff-v0.6'):
    output = Path(output).resolve()
    missing = [f for f in REQUIRED_IN_ARCHIVE if not (ROOT / f).exists()]
    if missing:
        raise SystemExit(f'Refusing to build an unlicensed archive. Missing: {missing}')
    if output.is_relative_to(ROOT):
        raise ValueError('Place the output archive outside the source directory')
    paths = []
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if not path.is_file() or path.is_symlink() or '__pycache__' in relative.parts:
            continue
        if published(path):
            paths.append(path)
    paths.sort()
    manifest = ROOT / 'MANIFEST.sha256'
    manifest.write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  '
                                f'{p.relative_to(ROOT).as_posix()}\n' for p in paths))
    paths.append(manifest)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(paths):
            info = zipfile.ZipInfo(f'{name}/{path.relative_to(ROOT).as_posix()}',
                                   date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    print(f'{output}: {len(paths)} files, {output.stat().st_size} bytes')
    print('SHA256 ' + hashlib.sha256(output.read_bytes()).hexdigest())
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--name', default='EHTLE-agent-handoff-v0.6')
    build(parser.parse_args().output, parser.parse_args().name)
