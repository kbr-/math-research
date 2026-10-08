#!/usr/bin/env python3
"""Verify the complete two-period cover and export its raw local algebra to GAP."""
import csv
import json
from pathlib import Path
P = Path('research/results/bmd-exception-outside-coverage-20261008')
def rows(name):
    records = list(csv.DictReader((P/name).open()))
    result = {int(r['degree_residue']): r for r in records}
    assert len(result) == len(records)
    return result
first = rows('permutation-verified.csv')
second = rows('second-full.csv')
assert set(first) == set(range(405))
failed = sorted(r for r, v in first.items() if int(v['rank']) < 188)
assert failed == [79, 155, 256, 332]
needed = {r for r in range(3240) if r % 405 in failed}
assert set(second) == needed and len(needed) == 32
assert all(int(r['rank']) == 188 for r in second.values())
assert all(int(first[r % 405]['rank']) == 188 or r in second for r in range(3240))
local = []
for suffix in ('', '-second'):
    data = list(map(int, (P/f'permutation-data{suffix}.txt').read_text().split()))
    assert data[:6] == [4, 1, 1, 1, 1, 1]
    selections = data[7:7+24*188]
    assert all(0 <= s < 460 for s in selections)
    phi = data[7+24*188:7+24*188+512]
    assert len(phi) == 512 and all(0 <= x < 81 for x in phi)
    local.append([data[1:6], data[6], phi])
(P/'local-certificates.g').write_text('LOCAL_CERTIFICATES := '+json.dumps(local)+';\n')
result = dict(first_degree_period=405, second_degree_period=3240,
              first_successes=401, first_residual=failed, fallback_classes=32,
              common_period=3240, covered_classes=3240, uncovered_classes=[],
              scope='Complete sufficient paired-boundary cover for n9,p3,d>=7; lower degrees use existing proof.')
(P/'coverage.json').write_text(json.dumps(result, indent=2)+'\n')
print('COMPLETE 3240/3240 degree classes covered; no unresolved class was discarded.')
