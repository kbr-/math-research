"""Joint kernel of the separated two-family Pang-form errors at K = 2, from the per-error transfer.

System: functional pigeonhole over F_2 (Booleanity, hole and functionality axioms, pigeon axioms
Q_i = 1 + sum_h x_ih, multilinear ring), m pigeons, N holes (8 unless --holes), D = 4. Everything is computed modulo H, the
closure of the hole and functionality axioms, which is the span of the non-matching monomials of degree <= D
(monomial axioms), so V_K mod H has the matching monomials of size <= K as basis.
Errors: q1 = x00 + x11, q2 = x22 + x33, E_e = (1 + q_nu) x_e for the edges e sharing no pigeon and no hole with
q_nu's edges (the separated family). A_e = Ann_H(E_e) cap V_K, computed as the kernel of u -> u E_e mod H.
W_K = C cap V_K mod H = span(B_K minus T_K) (the functional-transfer entry: C cap V_K is H cap V_K plus the lift
of K_K), spanned by Q_i at K = 1 and by Q_i and x_f Q_i at K = 2.
Statement used, not tested: by the entry's per-error transfer at K = 2 (N >= 8, 4 <= D <= ceil(N/2)), each
Ann_C(E_e) cap V_2 = A_e + W_2, so the joint C-kernel is J = intersection over e of (A_e + W_2).
Statement tested (the transfer form at K = 2): J = Z + W_2, where Z = intersection of the A_e, the domain joint
kernel; and Z = span{q1 q2}. The extreme the question needs: J contains Z + W_2 always, so the test is the
excess dim J - dim(Z + W_2) >= 0, compared with 0; no maximum over representatives enters.
Expected: excess 0 and dim Z = 1 at every m run with both families (a conjecture of this entry, written
before the run); for family 1 alone at K = 2 nothing is predicted, and its numbers are reported as found.
Refuted by: an excess of one or more at some m, or dim Z different from one at some m run here.
Possible because: per-error decompositions u = a_e + w_e with w_e depending on e can leave u outside Z + W_2,
as the elementary example A_1 = <a>, A_2 = <b>, W = <a - b> shows, and Z may hold other products.
Null control: K = 1 at the same boards, where cor:separated-family-kernels (c) proves J = W_1, of dimension m.
Refuted by: a K = 1 joint kernel of dimension other than m at some board run in this script.
Possible because: a wrong error list, a wrong product modulo H or a wrong W_1 would change that dimension.
Forced by counts: no count forces dim J at K = 1; J is an intersection of computed spaces of dimension 1 + mN.
Positive control: the elementary example above, A_1 = <x00>, A_2 = <x00 + Q_0>, W = <Q_0> in V_1, must give
excess 1 through the same intersection routine.
Refuted by: excess 0 on that example, which would mean the routine cannot see a transported killer at all.
Possible because: a remainder or kernel bug in the routine would hide every transported killer.
Also asserted, for part (d): q1 q2 lies in Z and not in W_2 at K = 2.
Also computed, for family 1 alone at K = 2 (the next attempt's candidate test, added after the review): the
excess dim(Z_1 + W_2) - dim(q1 V_1 + W_2) >= 0, q1 V_1 lying in Z_1 since q1(1 + q1) = 0; a positive excess gives
z1 in Z_1 outside q1 V_1 + W_2, and z1 q2 kills both families at K = 3. Not predicted; reported as found.
Baseline: the containments give dim J >= dim W_2 + 1 (W_2 and q1 q2) and dim J <= dim V_2; neither decides the
excess, and the summed condition is not used.
Record checked: cor:separated-family-kernels (K = 1, and q1 q2 at K = 2), lem:polynomial-numbering-transfer,
cor:two-factor-kernels and check:pang-family-kernels (K = 1 only); none gives J at K = 2.
"""
import argparse
import itertools
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from f2_span import Span

N = 8


class Board:
    def __init__(self, m, K):
        self.m, self.K = m, K
        self.edges = [(i, h) for i in range(m) for h in range(N)]
        self.bit = {e: 1 << k for k, e in enumerate(self.edges)}
        mats = [0]
        for size in range(1, K + 1):
            for es in itertools.combinations(self.edges, size):
                if self.matching(es):
                    mats.append(sum(self.bit[e] for e in es))
        self.basis = mats
        self.n = len(mats)
        self.index = {mm: k for k, mm in enumerate(mats)}

    def matching(self, es):
        return len({e[0] for e in es}) == len(es) and len({e[1] for e in es}) == len(es)

    def is_matching(self, mask):
        pigeons = holes = 0
        while mask:
            low = mask & -mask
            i, h = self.edges[low.bit_length() - 1]
            if pigeons >> i & 1 or holes >> h & 1:
                return False
            pigeons |= 1 << i
            holes |= 1 << h
            mask ^= low
        return True

    def times(self, p, q):
        """Product modulo H of two polynomials given as sets of monomial masks: non-matching monomials drop."""
        out = set()
        for a in p:
            for b in q:
                c = a | b
                if self.is_matching(c):
                    out ^= {c}
        return out

    def vec(self, poly):
        v = 0
        for mm in poly:
            v ^= 1 << self.index[mm]
        return v

    def Q(self, i):
        return {0} | {self.bit[(i, h)] for h in range(N)}

    def W(self):
        gens = [self.Q(i) for i in range(self.m)]
        if self.K == 2:
            gens += [self.times({self.bit[f]}, self.Q(i)) for i in range(self.m) for f in self.edges if f[0] != i]
        return [self.vec(g) for g in gens]

    def errors(self, families=(1, 2)):
        x = lambda i, h: self.bit[(i, h)]
        out = []
        if 1 in families:
            p1 = {0, x(0, 0), x(1, 1)}
            out += [self.times(p1, {x(*e)}) for e in self.edges if e[0] not in (0, 1) and e[1] not in (0, 1)]
        if 2 in families:
            p2 = {0, x(2, 2), x(3, 3)}
            out += [self.times(p2, {x(*e)}) for e in self.edges if e[0] not in (2, 3) and e[1] not in (2, 3)]
        return out


def kernel(n, images):
    """A basis of {c in F_2^n : sum c_k images[k] = 0}, images given as ints: rows of [image | identity] whose
    image part is zero after elimination, the identity in the low n bits so that image bits lead."""
    s = Span()
    for k, img in enumerate(images):
        s.add((img << n) | (1 << k))
    return [row for h, row in s.piv.items() if h < n]


def joint(n, A_list, W, Z):
    """dim of J, the intersection of the spaces A + W over A in A_list, against Z + W, Z being the intersection
    of the A (given); spaces are lists of ints over n coordinates. Remainders are taken modulo W once, then
    modulo each reduced A: u lies in A + W exactly when its W-remainder lies in the span of the W-remainders of
    A, by linearity of the canonical remainder."""
    sW = Span(W)
    rW = [sW.reduce(1 << k) for k in range(n)]
    images = [0] * n
    for e, A in enumerate(A_list):
        sA = Span([sW.reduce(a) for a in A])
        for k in range(n):
            images[k] |= sA.reduce(rW[k]) << (n * e)
    J = kernel(n, images)
    ZW = Span(Z + W)
    return {'dim_J': len(J), 'dim_Z': len(Z), 'dim_W': len(sW), 'dim_Z_plus_W': len(ZW),
            'excess': len(J) - len(ZW)}, J


def intersection(n, A_list):
    """The intersection of spaces given by bases, as the kernel of the stacked remainders (for small cases)."""
    images = [0] * n
    for e, A in enumerate(A_list):
        s = Span(A)
        for k in range(n):
            images[k] |= s.reduce(1 << k) << (n * e)
    return kernel(n, images)


def positive_control():
    b = Board(2, 1)
    x00, Q0 = b.vec({b.bit[(0, 0)]}), b.vec(b.Q(0))
    A_list = [[x00], [x00 ^ Q0]]
    q, _ = joint(b.n, A_list, [Q0], intersection(b.n, A_list))
    assert q['excess'] == 1, ('positive control failed', q)
    return q


def run(m, K, families=(1, 2)):
    t0 = time.time()
    b = Board(m, K)
    errs = b.errors(families)
    # the kernel of u -> u E mod H for each error, over the basis of V_K mod H
    A_list, zimages, zcols = [], [0] * b.n, {}
    for e, E in enumerate(errs):
        cols = {}
        images = []
        for k, mm in enumerate(b.basis):
            img = 0
            for c in b.times({mm}, E):
                img ^= 1 << cols.setdefault(c, len(cols))
                zimages[k] ^= 1 << zcols.setdefault((e, c), len(zcols))
            images.append(img)
        A_list.append(kernel(b.n, images))
    Z = kernel(b.n, zimages)
    W = b.W()
    q, J = joint(b.n, A_list, W, Z)
    q.update({'m': m, 'N': N, 'K': K, 'families': list(families), 'errors': len(errs), 'dim_V': b.n,
              'dims_A_e': sorted(set(len(A) for A in A_list)), 'seconds': round(time.time() - t0, 2)})
    if K == 2 and set(families) == {1, 2}:
        x = lambda i, h: b.bit[(i, h)]
        q1q2 = b.vec(b.times({x(0, 0), x(1, 1)}, {x(2, 2), x(3, 3)}))
        q['q1q2_in_Z'] = Span(Z).reduce(q1q2) == 0
        q['q1q2_in_W'] = Span(W).reduce(q1q2) == 0
        assert q['q1q2_in_Z'] and not q['q1q2_in_W'], 'part (d)'
    if K == 2 and tuple(families) == (1,):
        q1 = {b.bit[(0, 0)], b.bit[(1, 1)]}
        q1V1 = [b.vec(b.times(q1, {mm})) for mm in b.basis if bin(mm).count('1') <= 1]
        assert all(Span(Z).reduce(v) == 0 for v in q1V1), 'q1 V_1 lies in Z_1'
        q['dim_q1V1_plus_W'] = len(Span(q1V1 + W))
        q['family1_excess_over_q1V1'] = q['dim_Z_plus_W'] - q['dim_q1V1_plus_W']
    return q


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--pigeons', default='4,5,6')
    ap.add_argument('--holes', type=int, default=8)
    args = ap.parse_args()
    global N
    N = args.holes
    out = {'positive_control': positive_control(), 'runs': []}
    for m in [int(t) for t in args.pigeons.split(',')]:
        null = run(m, 1)
        assert null['dim_J'] == m, ('null control', null)
        out['runs'].append(null)
        for fams in ((1, 2), (1,)):
            out['runs'].append(run(m, 2, fams))
            print(json.dumps(out['runs'][-1]), flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
