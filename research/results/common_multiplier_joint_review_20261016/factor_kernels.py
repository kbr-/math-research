"""Falsification check for the joint-savings review: factor annihilators and hole neighbourhoods.

Setting: pigeonhole systems over F_2 (pigeon axioms prod_j(1+x_ij), hole axioms x_ij x_kj), multilinear
ring, degree-D closure C by tools/pc_closure.py, K=1, V_1 = span(1, x_ij).  For single-variable inputs
g1, g2 the two Pang-form errors (1+g1+g2) g_i both equal g1 g2 in the multilinear ring, so a family's
kernel is Z(g1,g2) = {u in V_1 : g1 g2 u in C}, and Ann(w) = {u in V_1 : w u in C}.

Statements tested:
 (A) at 4 pigeons, 3 holes, D=3, the stacked kernel of the six families of the truncated-quotient
     check equals Ann(x_00): its joint saving is domination by the shared input.
 (B) at 5 pigeons, 4 holes, D=3, for all families (x_00, y), y not in hole 0, the stacked kernel equals
     Ann(x_00), of dimension 5 (1+x_00 and the other pigeons' hole-0 variables).
 (C) same instance, families (x_i0, y) for i in I={0,1} and every y outside hole 0: no single input is
     shared, yet the stacked kernel equals span{x_k0 : k not in I}, of dimension 3, while the summed
     codimensions exceed dim V_1.
Expected: (A), (B), (C) hold as stated; the script asserts them and prints PASS.
Refuted by: a stacked kernel strictly larger or smaller than the predicted span in (A), (B) or (C).
Possible because: the closure at D=3 may contain further degree-3 members (pigeon-axiom products) that
kill more classes, or the hole-axiom multiples may fail to reach degree 3 inside the closure.
"""
import argparse
import itertools
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import pc_closure as pc


def php(m, n):
    v = lambda i, j: i * n + j
    axioms = []
    for i in range(m):
        p = {0}
        for j in range(n):
            p = pc.multiply(p, {0, 1 << v(i, j)})
        axioms.append(p)
    for j in range(n):
        for i, k in itertools.combinations(range(m), 2):
            axioms.append({(1 << v(i, j)) | (1 << v(k, j))})
    return axioms, m * n, v


def kernel(c, nv, polys_of_u):
    """Kernel in V_1 (basis 1, x_0..x_{nv-1}) of u -> (remainders of p u for p in polys_of_u), over F_2."""
    basis = [{0}] + [{1 << i} for i in range(nv)]
    rows = []
    for b in basis:
        vec = 0
        shift = 0
        for p in polys_of_u:
            r = c.reduce(c.vector(pc.multiply(p, b)))
            vec |= r << shift
            shift += len(c.monos)
        rows.append(vec)
    # Gaussian elimination on [image | identity] to read the kernel.
    width = len(basis)
    aug = [(rows[i], 1 << i) for i in range(width)]
    pivots = {}
    kern = []
    for img, ident in aug:
        while img:
            p = img.bit_length() - 1
            if p in pivots:
                img ^= pivots[p][0]
                ident ^= pivots[p][1]
            else:
                pivots[p] = (img, ident)
                break
        if not img:
            kern.append(ident)
    return kern, width


def span_dim(vecs):
    piv = {}
    for v in vecs:
        while v:
            p = v.bit_length() - 1
            if p in piv:
                v ^= piv[p]
            else:
                piv[p] = v
                break
    return len(piv)


def same_span(a, b):
    return span_dim(a) == span_dim(b) == span_dim(a + b)


def coord(i):
    """Vector in V_1 coordinates for the variable x_i (coordinate i+1); coordinate 0 is the constant."""
    return 1 << (i + 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = {}

    axioms, nv, v = php(4, 3)
    c = pc.Closure(axioms, nv, 3)
    assert c.proper
    x00 = 1 << v(0, 0)
    fams = [(x00, 1 << v(0, 1)), (x00, 1 << v(0, 2)), (x00, 1 << v(1, 0)), (x00, 1 << v(1, 1)),
            (x00, 1 << v(1, 2)), (x00, 1 << v(2, 0))]
    stacked, w = kernel(c, nv, [{a | b} for a, b in fams])
    ann, _ = kernel(c, nv, [{x00}])
    out['A'] = dict(dim_V1=w, stacked_kernel=span_dim(stacked), ann_x00=span_dim(ann),
                    equal=same_span(stacked, ann))
    print('A', out['A'], flush=True)
    assert out['A']['equal'] and out['A']['stacked_kernel'] == 4

    axioms, nv, v = php(5, 4)
    c = pc.Closure(axioms, nv, 3)
    assert c.proper
    others = [1 << v(i, j) for i in range(5) for j in range(1, 4)]
    x00 = 1 << v(0, 0)
    stacked, w = kernel(c, nv, [{x00 | y} for y in others])
    ann, _ = kernel(c, nv, [{x00}])
    single = [kernel(c, nv, [{x00 | y}])[0] for y in others]
    out['B'] = dict(dim_V1=w, families=len(others), stacked_kernel=span_dim(stacked), ann_x00=span_dim(ann),
                    equal=same_span(stacked, ann),
                    summed_codim=sum(w - span_dim(k) for k in single))
    print('B', out['B'], flush=True)
    assert out['B']['equal'] and out['B']['stacked_kernel'] == 5

    I = (0, 1)
    fams = [(1 << v(i, 0)) | y for i in I for y in others]
    stacked, w = kernel(c, nv, [{f} for f in fams])
    predicted = [coord(v(k, 0)) for k in range(5) if k not in I]
    single = [kernel(c, nv, [{f}])[0] for f in fams]
    out['C'] = dict(dim_V1=w, families=len(fams), stacked_kernel=span_dim(stacked),
                    predicted=span_dim(predicted), equal=same_span(stacked, predicted),
                    summed_codim=sum(w - span_dim(k) for k in single),
                    ann_x00_cap_ann_x10=span_dim(kernel(c, nv, [{1 << v(0, 0)}, {1 << v(1, 0)}])[0]))
    print('C', out['C'], flush=True)
    assert out['C']['equal'] and out['C']['stacked_kernel'] == 3
    assert out['C']['summed_codim'] > w
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')
    print('PASS')


if __name__ == '__main__':
    main()
