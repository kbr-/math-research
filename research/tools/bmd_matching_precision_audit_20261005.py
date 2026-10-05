#!/usr/bin/env python3
"""Certify errors of the four fixed matching determinants by assignment bounds.

Every omitted entry has u-valuation >= P. Force one error position, then use
SciPy's compiled linear assignment solver for the remaining determinant term.
All weights/costs are small exact integers; no floating-point rank is used.
If cancellation makes the assignment bound too weak, PARI computes the exact
cofactors modulo u^P; terms with two errors have order at least 2P.
"""
import argparse
import itertools
import json
import re
import subprocess
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
cases = []
current = None
for line in args.input.read_text().splitlines():
    if line.startswith('case e='):
        current = {key: int(value) for key, value in re.findall(r'(e|c|dim|precision)=(\d+)', line)}
    elif line.startswith('matrix='):
        current['matrix'] = line.split('=', 1)[1]
    elif line.startswith('valuations='):
        raw = line.split('=', 1)[1].strip().strip('[]')
        current['weights'] = [[int(x.strip()) for x in row.split(',')] for row in raw.split(';')]
    elif line.startswith('leading_order='):
        current['leading_order'] = int(re.search(r'leading_order=(\d+)', line)[1])
        cases.append(current)
        current = None
assert len(cases) == 4, 'Expected exactly four completed determinant certificates'
results = []
for case in cases:
    weights = np.array(case['weights'], dtype=np.int64)
    n = case['dim']
    assert weights.shape == (n, n)
    assert np.all((weights >= 0) & (weights <= case['precision']))
    costs = np.zeros((n, n), dtype=np.int64)
    for i, j in itertools.product(range(n), repeat=2):
        reduced = np.delete(np.delete(weights, i, axis=0), j, axis=1)
        rows, cols = linear_sum_assignment(reduced)
        assert len(set(rows)) == n - 1 and len(set(cols)) == n - 1
        costs[i, j] = int(reduced[rows, cols].sum())
    bound = case['precision'] + int(costs.min())
    exact_values = None
    if case['leading_order'] >= bound:
        # The assignment bound ignores cancellations. Certify exact cofactors;
        # terms with >=2 entry errors have order >=2P since entries are regular.
        assert 'a' not in case['matrix'], 'Expected prime-field matrix coefficients'
        prec = case['precision']
        gp = f"""default(parisizemax,1000000000); default(parisize,134217728);
u; o=Mod(1,3);
F={case['matrix']};
FP=matrix({n},{n},i,j,o*lift(F[i,j]));
EX=matdet(FP);
if(valuation(EX,u)!={case['leading_order']},error("leading order changed under input reconstruction"));
FS=matrix({n},{n},i,j,FP[i,j]+O(u^{prec}));
AD=matrix({n},{n},i,j,(-1)^(i+j)*matdet(matrix({n-1},{n-1},r,c,FS[r+(r>=j),c+(c>=i)])));
CHK=FS*AD-matdet(FS)*matid({n});
for(i=1,{n},for(j=1,{n},if(valuation(CHK[i,j],u)<{prec},error("truncated adjugate identity"))));
print("COFACTORS=",matrix({n},{n},i,j,min({prec},valuation(AD[i,j],u))));
quit;
"""
        proc = subprocess.run(['gp', '-q', '-f'], input=gp, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        lines = [line for line in proc.stdout.splitlines() if line.startswith('COFACTORS=')]
        assert len(lines) == 1 and 'at top-level' not in proc.stderr, proc.stdout + proc.stderr
        raw = lines[0].split('=', 1)[1].strip().strip('[]')
        exact_values = [[int(x.strip()) for x in row.split(',')] for row in raw.split(';')]
        bound = min(2 * prec, prec + min(map(min, exact_values)))
    assert case['leading_order'] < bound, 'Leading term exceeds the certified error bound'
    result = {key: case[key] for key in ('e', 'c', 'dim', 'precision', 'leading_order')}
    result.update(error_order_at_least=bound, cofactor_costs=costs.tolist(),
                  exact_cofactor_orders=exact_values)
    results.append(result)
    print(f"PASS c={case['c']} leading={case['leading_order']} < error bound={bound}")
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps({'passed': True, 'cases': results}, indent=2) + '\n')
