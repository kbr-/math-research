"""Smallest case of the next attempt: one native functional over F_2 modulo a proper closure, at K = L = 1.

System: functional pigeonhole over F_2, 6 pigeons, 5 holes, multilinear, D = 3 (C proper, asserted as in
dense_linear.py), error E = sum_{j<5} x_jj, K = 1, L = 1. An old functional is a linear functional on V_3 vanishing
on C, so mu(p) = parity of (remainder of p modulo C) & mask, for a mask over the remainder's coordinates. Its
rectangle form is M_mu(u, v) = mu(E u v), u, v in V_1; mu detects Ann_C(E) cap V_1 exactly when rank M_mu equals the
rank r of u -> [uE] modulo C, which is 31 - 7 = 24 (dense_linear.json).
Statement tested: the untested question whether one F_2 functional detects the kernel here (the record brackets
the least number between ceil(r / dim Z_1) = 1 and r = 24; thm:common-moment-radical gives one functional only over
an extension of size above 2r + 1).
Expected: no expectation is predicted; the script prints the largest rank over 500 random masks and whether 24 is
reached.
Refuted by: no single functional reaching rank 24 among the masks, which leaves the case open, not refuted.
Possible because: over F_2 the symmetric forms of one functional may all be degenerate on this space.
Control: for E = x00 (rank 31 - 15 = 16 by dense_linear.json) the same search is run and its largest rank printed.
Forced by counts: nothing; M_mu is 31 by 31 and the rank of interest is 24, so no row count decides it.
Refuted by: a largest rank above the rank r of the error, which is impossible and would mean a bug.
Possible because: a wrong remainder or mask would give ranks unrelated to r.
Positive control: rank M_mu never exceeds r for any mask (asserted), the left kernel containing Ann_C(E).
Baseline: the recorded bracket [1, 24] and thm:common-moment-radical over a large extension.
Record checked: the claims read were lem:native-detection-count and thm:common-moment-radical; neither decides
one functional over F_2 itself.
"""
import argparse
import importlib.util
import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import pc_closure as pc
import f2_span

spec = importlib.util.spec_from_file_location(
    'three_quantities', ROOT / 'research/results/common_multiplier_transfer_test_20261016/three_quantities.py')
tq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tq)


def best_rank(cC, monos, E, trials, rng):
    prods = [[tq.red(cC, cC.vector(pc.multiply(pc.multiply({u}, set(E)), {v}))) for v in monos] for u in monos]
    width = max(x.bit_length() for row in prods for x in row) + 1
    best = 0
    for _ in range(trials):
        mask = rng.getrandbits(width)
        rows = [sum(((bin(x & mask).count('1') & 1) << k) for k, x in enumerate(row)) for row in prods]
        best = max(best, len(f2_span.Span(rows)))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    mono, full, nv, v = tq.systems(6, 5)
    cC = tq.prepare(pc.Closure(full, nv, 3))
    assert cC.proper
    monos = [m for m in cC.monos if tq.deg(m) <= 1]
    assert len(monos) == 31
    x = lambda i, j: 1 << v(i, j)
    rng = random.Random(17)
    out = {}
    for name, E, r in (('E1', {x(j, j) for j in range(5)}, 24), ('x00', {x(0, 0)}, 16)):
        b = best_rank(cC, monos, E, 500, rng)
        assert b <= r, 'positive control: rank at most r'
        out[name] = {'r': r, 'best_rank_500_masks': b, 'one_functional_detects': b == r}
        print(name, out[name], flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
