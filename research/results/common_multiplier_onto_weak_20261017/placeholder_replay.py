"""Replay of tools/claim_authoring.py's draft-placeholder pattern over every committed claim spec, and a count of
spec assessments that credit a reviewer.

No statement tested: a count of the records a check reads, its refusals listed so each can be judged against its
source (AGENTS.md: a check is replayed over the record before its commit).
"""
import glob
import json
import sys

sys.path.insert(0, 'tools')
from claim_authoring import PLACEHOLDER, _spec_texts  # noqa: E402

specs = sorted(glob.glob('research/results/*/claim-spec*.json') + glob.glob('research/results/*/*spec*.json'))
specs = sorted(set(specs))
refused, crediting, checked = [], 0, 0
for path in specs:
    try:
        spec = json.load(open(path))
    except (ValueError, OSError):
        continue
    if not isinstance(spec, dict) or 'claims' not in spec:
        continue
    checked += 1
    marks = sorted({m for text in _spec_texts(spec) for m in PLACEHOLDER.findall(text)})
    if marks:
        refused.append((path, marks))
    crediting += sum('reviewer' in str(c.get('assessment', '')) for c in spec['claims'])
print(f'{len(specs)} spec files found, {checked} of them claim specs checked; {len(refused)} refused by the '
      'placeholder pattern:')
for path, marks in refused:
    print(' ', path, marks)
print(f'{crediting} claim assessments in them credit a reviewer')
