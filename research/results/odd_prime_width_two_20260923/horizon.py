"""Computational horizon for width-2 clause tests: column counts of the recorded closure space QSpace(n, D) (all
monomials of degree <= D, and those of degree D), with the dense-basis memory 2*cols*ceil(cols/64)*8 bytes, and whether
the base (weak unary PHP^{n+1}_n) alone is refuted by its degree-D closure where that closure is affordable.
Usage: python3 horizon.py --out OUT.json"""
import argparse, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_local_falls_20260923'))
from local_falls import Closure, QSpace, base_rows
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args(); res = []
for n, D, close in ((6, 3, True), (5, 4, True), (5, 5, True), (6, 4, True), (6, 5, False), (7, 5, False)):
    t = time.time(); sp = QSpace(n, D); top = int((sp.deg == D).sum()); gb = 2 * sp.cols * ((sp.cols + 63) // 64) * 8 / 1e9
    r = dict(n=n, D=D, columns=int(sp.cols), top_columns=top, dense_basis_GB=round(gb, 2))
    if close:
        C = Closure(sp, 12); C.add(base_rows(n)); r['base'] = C.split()
    r['seconds'] = round(time.time() - t, 1); res.append(r); print(r, flush=True)
    json.dump(res, open(a.out, 'w'), indent=1)
