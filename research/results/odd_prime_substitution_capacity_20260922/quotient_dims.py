"""Quotient dimensions d_k = dim(R_{<=k} / C_k(PHP)) of ordinary weak unary PHP^{n+1}_n over F_3, in the
collision quotient, for the counting heuristic: an affine equation's degree-D constraints are its
multiples by degree <= D-1, so M equations exhaust the design space near M ~ d_D / d_{D-1}.
Usage: quotient_dims.py --out PATH   (sizes are fixed below; all run in seconds)"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_one_count_20260922'))
from random_conditioning_fast import QSpace, closure_of, base_rows
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
out = []
for n, D in [(n, 2) for n in range(4, 11)] + [(5, 3), (6, 3), (7, 3)]:
    row = {'n': n, 'D': D}
    for k in (D - 1, D):
        sp = QSpace(n, k); P, W, piv = closure_of(sp, base_rows(n))
        row[f'd_{k}'] = sp.cols - P.shape[0]
    row['ratio'] = round(row[f'd_{D}'] / row[f'd_{D-1}'], 2)
    row['law'] = (n + 1 - 2 * D) * (n - 1) + 1
    print(row, flush=True); out.append(row)
json.dump(out, open(a.out, 'w'), indent=1)
