"""Build a reproducible source/results ZIP after running `python3 -m ehtle verify`."""
import argparse
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {'README.md', 'HANDOFF.md', 'AGENTS.md', 'pyproject.toml', '.gitignore'}
DIRECTORIES = {'ehtle', 'tests', 'examples', 'agents', 'docs', 'compat', 'scripts', 'results'}
SUFFIXES = {'.py', '.md', '.json', '.toml', '.zip'}

def build(output):
    output = Path(output).resolve()
    if output.is_relative_to(ROOT):
        raise ValueError('Place the output archive outside the source directory')
    paths = []
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if not path.is_file() or path.is_symlink() or '__pycache__' in relative.parts:
            continue
        if str(relative) in ROOT_FILES or (relative.parts[0] in DIRECTORIES and path.suffix in SUFFIXES):
            # Package the verified fixtures, not ad-hoc local model runs.
            if relative.parts[0] == 'results' and relative.parts[1] != 'verification':
                continue
            paths.append(path)
    paths.sort()
    manifest = ROOT / 'MANIFEST.sha256'
    manifest.write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n' for p in paths))
    paths.append(manifest)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(paths):
            name = 'EHTLE-agent-handoff-v0.5/' + path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 29, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    print(f'{output}: {len(paths)} files, {output.stat().st_size} bytes')
    print('SHA256 ' + hashlib.sha256(output.read_bytes()).hexdigest())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    build(parser.parse_args().output)
