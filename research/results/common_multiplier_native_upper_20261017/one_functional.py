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
Second instance: E = x00, with no predicted failure. (Second run, after the review: r is computed here, in the
same closure, as the rank of u -> remainder(Eu) on the 31 monomials of V_1, and asserted against the values 24 and
16 of dense_linear.json; the mask reaching rank r is saved. The first run's output is one_functional_run1.json.)
Control: a mask's rectangle form never exceeds rank r, the left kernel containing Ann_C(E) cap V_1; asserted.
Forced by counts: nothing; M_mu is 31 by 31 and the rank of interest is 24, so no row count decides it.
Refuted by: a rank above r for some mask, which is impossible and would mean a bug in the remainders.
Possible because: a wrong remainder or mask would give ranks unrelated to r.
No positive control: the effect sought, a full-rank form, is what the search measures; no instance is known in
advance to have it.
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


def error_rank(cC, monos, E):
    """r: the rank of u -> remainder of uE modulo C on the monomials of V_1, in this closure."""
    return len(f2_span.Span([tq.red(cC, cC.vector(pc.multiply({u}, set(E)))) for u in monos]))


def best_rank(cC, monos, E, trials, rng):
    prods = [[tq.red(cC, cC.vector(pc.multiply(pc.multiply({u}, set(E)), {v}))) for v in monos] for u in monos]
    width = max(x.bit_length() for row in prods for x in row) + 1
    best, witness = 0, None
    for _ in range(trials):
        mask = rng.getrandbits(width)
        rows = [sum(((bin(x & mask).count('1') & 1) << k) for k, x in enumerate(row)) for row in prods]
        rank = len(f2_span.Span(rows))
        if rank > best:
            best, witness = rank, mask
    return best, witness


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
        r_here = error_rank(cC, monos, E)
        assert r_here == r, ('r computed in this closure', r_here, r)
        b, mask = best_rank(cC, monos, E, 500, rng)
        assert b <= r, 'control: rank at most r'
        out[name] = {'r': r_here, 'best_rank_500_masks': b, 'one_functional_detects': b == r_here,
                     'witness_mask_over_remainder_coordinates': hex(mask)}
        print(name, out[name], flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
