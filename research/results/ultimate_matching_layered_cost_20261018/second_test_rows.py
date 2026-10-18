"""Tabulate lem:completion-failure-certificate's second test at every recorded level of the box-level runs.

No statement tested: it reads the saved outputs of research/results/ultimate_matching_box_completion_20261018
(box_completion_4096.json, box_completion.json), whose box_completion.py records per level m and, at a level
with a drop, nuD = nu(G_(k+1)[D_X u D_Y]) and nuD_below_drop; it prints m_k, m_(k+1), the drop and nuD so that the
test nuD < m_k - m_(k+1), which refutes completion with C = 1 for every maximum matching, is read beside its
inputs. Run: python3 second_test_rows.py > second_test_rows.txt from the repository root.
"""
import json
from pathlib import Path

base = Path('research/results/ultimate_matching_box_completion_20261018')
print('lem:completion-failure-certificate second test, nu(G_(k+1)[D_X u D_Y]) < m_k - m_(k+1), read from the saved outputs of')
print(base, '(box_completion_4096.json, box_completion.json): N L seed level m_k m_(k+1) drop nuD nuD_below_drop')
for f in ['box_completion_4096.json', 'box_completion.json']:
    for s in json.load(open(base / f))['samples']:
        lv = s['levels']
        for a, b in zip(lv, lv[1:]):
            if 'nuD' in a:
                print(s['N'], s['L'], s['seed'], a['k'], a['m'], b['m'], a['m'] - b['m'], a['nuD'], a['nuD_below_drop'])
