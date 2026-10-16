"""Decisive test of the joint-savings goal review, on the product pigeonhole system at its top degree.

System: product pigeonhole over F_2, m = 4 pigeons, n = 3 holes, multilinear ring: pigeon axioms
prod_j (1 + x_ij) (degree 3) and hole axioms x_ij x_kj (degree 2); C its degree-3 closure, proper
(lem:top-degree-axiom-inertness: below degree 3 it is the vanishing ideal of the hole-respecting set Y).
Window D-K = 2, K = 1, T = 1, deg nu = 1, room 2+1 = 3 = D' (tight).  Twisted variable x_1 = x_00.

For an error set S (variables other than x_00) with protected weight w = x_00, a coordinate of a
twisted repair is a pair (c, f_1), f_1 = (rho(x_1) nu)_l, with conditions linear in f_1:
soundness at the hole axioms x_00 x_k0 (k = 1, 2, 3) gives x_k0 f_1 in C, killing of x_00 E gives
E f_1 in C, and survival is f_1 not in C (hole axioms free of x_00, and killing, put no condition on c
at degree <= 3).  F_S denotes {f in V_2 : p f in C for p in {x_10, x_20, x_30} + S}.

Comparison class (the review's, corrected by its follow-up): substitution x_00 -> r times a multiplier
m of degree <= deg nu = 1, i.e. pairs (m, r m) with r, m linear (r = x_00 is the scalar repair m).  A
twisted repair beyond it needs a survivor of F_S that no single product r m of linear forms gives.

Statement tested (an untested hypothesis, stated so it can fail): for every nonempty S, F_S has a
survivor (an element not in C) only if it has a survivor of the form r m, r and m linear.
Expected: no gap for any S; the script prints the number of sets with a survivor, with a product
survivor, and the gap sets (expected none).
Refuted by: a set S whose F_S contains a survivor while no product r m in F_S survives.
Possible because: degree-3 memberships at the top degree (restriction to Y lying in the span of the
unplaced-pigeon indicators) can hold for a sum of products when they hold for no single product.
Positive control: a synthetic closure on y1..y4, v with the one axiom v(y1 y2 + y3 y4) at D = 3 and
conditions {v}: y1 y2 + y3 y4 survives and no product of linear forms does, so the gap must be seen.
Refuted by: the control reporting no gap, which would mean the search cannot see one.
Possible because: a bug in the product enumeration or in the survivor test would hide it.
Control: S = {x_01} must have the product survivor x_00 * x_11 (the scalar repair m = x_11), asserted.
Decisive at these sizes: the outcome is exact (a gap set exists or not), with no seeds or spread; the
board with four pigeons and three holes is the smallest proper top-degree instance with tight room.
Parallel use: one process; the sets are independent, but most exit at the first product found, and
only a gap set runs the full enumeration of 8191 multipliers.
Baseline: scalar repairs of degree <= 1 (r = x_00) are the plainest class; the script prints for how
many sets one exists, which decides the expectation for those sets only.
"""
import argparse
import itertools
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import pc_closure as pc


class Reducer:
    """Canonical remainder modulo a closure, with the pivot order computed once."""

    def __init__(self, closure):
        self.c = closure
        self.order = sorted(closure.rows)

    def rem(self, poly):
        v = self.c.vector(poly)
        for p in self.order:
            if v >> p & 1:
                v ^= self.c.rows[p]
        return v


def kernel(images):
    """Basis (as combination bit masks over the inputs) of the kernel of the given image vectors."""
    pivots, kern = {}, []
    for i, img in enumerate(images):
        ident = 1 << i
        while img:
            top = img.bit_length() - 1
            if top in pivots:
                img ^= pivots[top][0]
                ident ^= pivots[top][1]
            else:
                pivots[top] = (img, ident)
                break
        if not img:
            kern.append(ident)
    return kern


def combine(basis, mask):
    out = set()
    for i, b in enumerate(basis):
        if mask >> i & 1:
            out ^= b
    return out


def survivors(red, conds, basis):
    """Whether some f in span(basis) with p f in C for all p in conds lies outside C."""
    shift = len(red.c.monos)
    images = []
    for b in basis:
        vec = 0
        for j, p in enumerate(conds):
            vec |= red.rem(pc.multiply(p, b)) << (j * shift)
        images.append(vec)
    return any(red.rem(combine(basis, k)) for k in kernel(images))


def product_survivor(red, conds, linear):
    """A pair (r, m) of linear forms with r m in F (conditions conds) and r m outside C, or None."""
    shift = len(red.c.monos)
    for mmask in range(1, 1 << len(linear)):
        m = combine(linear, mmask)
        rb = [pc.multiply(b, m) for b in linear]
        images = []
        for f in rb:
            vec = 0
            for j, p in enumerate(conds):
                vec |= red.rem(pc.multiply(p, f)) << (j * shift)
            images.append(vec)
        for k in kernel(images):
            f = combine(rb, k)
            if red.rem(f):
                return combine(linear, k), m
    return None


def show(poly, names):
    return ' + '.join('*'.join(names[i] for i in range(len(names)) if mono >> i & 1) or '1'
                      for mono in sorted(poly)) or '0'


def product_php(m, n):
    v = lambda i, j: i * n + j
    axioms = [{(1 << v(i, j)) | (1 << v(k, j))} for j in range(n) for i, k in itertools.combinations(range(m), 2)]
    for i in range(m):
        poly = {0}
        for j in range(n):
            poly = pc.multiply(poly, {0, 1 << v(i, j)})
        axioms.append(poly)
    return axioms, m * n, v


def positive_control():
    nv = 5                        # y1..y4 = bits 0..3, v = bit 4
    axiom = pc.multiply({1 << 4}, {(1 << 0) | (1 << 1), (1 << 2) | (1 << 3)})
    red = Reducer(pc.Closure([axiom], nv, 3))
    linear = [{0}] + [{1 << i} for i in range(nv)]
    quad = pc.monomials(nv, 2)
    conds = [{1 << 4}]
    surv = survivors(red, conds, [{q} for q in quad])
    prod = product_survivor(red, conds, linear)
    return surv, prod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    surv, prod = positive_control()
    print(f'positive control: survivor {surv}, product survivor {prod}', flush=True)
    assert surv and prod is None, 'positive control: the gap must be seen'
    axioms, nv, v = product_php(4, 3)
    closure = pc.Closure(axioms, nv, 3)
    assert closure.proper
    red = Reducer(closure)
    names = [f'x{i}{j}' for i in range(4) for j in range(3)]
    linear = [{0}] + [{1 << i} for i in range(nv)]
    quad = [{q} for q in pc.monomials(nv, 2)]
    x1 = v(0, 0)
    base = [{1 << v(k, 0)} for k in (1, 2, 3)]
    others = [i for i in range(nv) if i != x1]
    print(f'closure dim {closure.dim}, monomials {len(closure.monos)}, sets {2 ** len(others) - 1}', flush=True)
    rows, gaps, with_surv, with_prod, with_scalar = [], [], 0, 0, 0
    for size in range(1, len(others) + 1):
        for S in itertools.combinations(others, size):
            conds = base + [{1 << e} for e in S]
            s = survivors(red, conds, quad)
            scalar = survivors(red, conds, [pc.multiply({1 << x1}, b) for b in linear])
            p = product_survivor(red, conds, linear) if s else None
            with_surv += s
            with_scalar += scalar
            with_prod += p is not None
            row = {'S': [names[e] for e in S], 'survivor': s, 'scalar_degree1': scalar,
                   'product': None if p is None else [show(p[0], names), show(p[1], names)]}
            rows.append(row)
            if s and p is None:
                gaps.append(row)
                print('GAP', row, flush=True)
    single = {tuple(r['S']): r for r in rows if len(r['S']) == 1}
    assert single[('x01',)]['product'] is not None, 'control: S={x01} has a product survivor'
    summary = {'sets': len(rows), 'with_survivor': with_surv, 'with_product_survivor': with_prod,
               'with_scalar_degree1': with_scalar, 'gaps': gaps}
    print(json.dumps({k: (len(v) if k == 'gaps' else v) for k, v in summary.items()}), flush=True)
    pathlib.Path(args.out).write_text(json.dumps({'summary': summary, 'rows': rows}, indent=1) + '\n')
    print('PASS' if not gaps else 'REFUTED: gaps found', flush=True)


if __name__ == '__main__':
    main()
