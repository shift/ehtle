"""Backfill the pass/fail verdict into published run summaries.

Summaries written before `ehtle.reporting.verdict` existed carry no verdict, so a reader of the
archive sees aggregates with no answer attached. This recomputes the verdict from the episodes that
are on disk -- it does not re-run anything and it does not alter a single score.

    python3 scripts/add_verdicts.py results/*/summary.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ehtle.reporting import aggregate, interpret_zero, verdict  # noqa: E402


def episodes(directory):
    traces = []
    for path in sorted(directory.glob('*.json')):
        if path.name in ('summary.json', 'run_record.json', 'probes.json', 'statistics.json',
                         'bridge-transport-check.json'):
            continue
        payload = json.loads(path.read_text())
        if isinstance(payload, dict) and 'score' in payload and 'commit_attempts' in payload['score']:
            traces.append(payload['score'])
    return traces


def main(paths):
    changed = skipped = 0
    for name in paths:
        summary_path = Path(name)
        directory = summary_path.parent
        if not summary_path.exists():
            print(f'  skip (no summary): {name}')
            skipped += 1
            continue
        if 'verdict' in json.loads(summary_path.read_text()):
            print(f'  already has a verdict: {name}')
            skipped += 1
            continue
        existing = json.loads(summary_path.read_text())
        # A fixture directory deliberately mixes policies that are meant to behave differently.
        # Aggregating them into one verdict produces a meaningless number -- a corpus that
        # contains both the reference policy and four shortcuts is not a system.
        if 'policies' in existing and existing.get('kind') != 'model_run':
            print(f'  skip (mixed-policy fixture corpus, per-policy verdicts already present): '
                  f'{name}')
            skipped += 1
            continue
        traces = episodes(directory)
        if not traces:
            print(f'  skip (no episodes): {name}')
            skipped += 1
            continue
        overall = aggregate(traces)
        scored = verdict(overall)
        summary = existing
        summary['verdict'] = scored
        summary['verdict_interpretation'] = interpret_zero(overall, scored)
        summary['verdict_provenance'] = (
            'Backfilled by scripts/add_verdicts.py from the episode traces in this directory. No '
            'episode was re-run and no score was altered. The verdict logic is in '
            'ehtle/reporting.py and is the same code every new run uses.')
        summary_path.write_text(json.dumps(summary, indent=2) + '\n')
        print(f'  {summary_path}: {scored["verdict"]} ({scored["failed_count"]} failed, '
              f'{scored["episodes"]} episodes)')
        changed += 1
    print(f'{changed} summaries updated, {skipped} skipped')


if __name__ == '__main__':
    main(sys.argv[1:] or ['results'])
