"""Dimensions d_j of the weak unary PHP base's degree-j PC quotient over F_3 (collision-free multilinear
monomials modulo the degree-j closure of the row equations), for the capacity-count comparison.
Usage: quotient_dims.py --n N --jmax J --out PATH"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_one_count_20260922'))
from random_conditioning_fast import QSpace, closure_of, base_rows
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int); ap.add_argument('--jmax', type=int); ap.add_argument('--out')
a = ap.parse_args(); res = {'n': a.n, 'd': {}}
for j in range(0, a.jmax + 1):
    sp = QSpace(a.n, j); P, W, piv = closure_of(sp, base_rows(a.n))
    res['d'][j] = {'columns': sp.cols, 'rank': int(P.shape[0]), 'quotient_dim': int(sp.cols - P.shape[0])}
    print(a.n, j, res['d'][j], flush=True)
json.dump(res, open(a.out, 'w'), indent=1)
