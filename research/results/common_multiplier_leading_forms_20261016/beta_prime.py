"""The sharpened leading-form bound beta' against the least surviving common killer, on a proper closure.

System: functional pigeonhole over F_2 (pigeon axioms 1 + sum_j x_ij, hole and functionality axioms), the
multilinear ring, 6 pigeons and 5 holes at D = 3, proper (check:functional-factor-kernels). G = F[x]/(x_v^2),
T_k the top parts of members of degree exactly k. For an error set F of degree e and a <= D - e,
beta'(F) is the least a with some g in G_a outside T_a and g * top(E) in T_(a+e) for every E in F
(product in G); k*(F) is the least k <= D - e with some f in V_k, f not in C, f E in C for every E in F.

Statement tested (lem:leading-form-killer-bound, sharpened form): beta'(F) <= k*(F) for every F, as the
reduction "subtract a member with the same top part" proves; and an untested hypothesis on vacuity:
for single-variable error sets, beta' equals k*.
Expected: beta' <= k* for every F (asserted), and beta' = k* for the listed sets; the script prints both.
Refuted by: some F with beta' > k*, which would contradict the reduction lemma and mean an error in it.
Possible because: the multilinear product may lower degree in a way the graded product in G misses.
Control: F = {1} (a constant error) has no surviving killer, k* undefined, and beta' undefined; asserted.
Refuted by: a reported surviving killer of the constant error, which would mean the closure reports 1 in C.
Possible because: a bug in the membership of f * 1 would let a non-member pass.
"""
import argparse
import itertools
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import pc_closure as pc


def functional_php(m, n):
    v = lambda i, j: i * n + j
    axioms = []
    for j in range(n):
        for i, k in itertools.combinations(range(m), 2):
            axioms.append({(1 << v(i, j)) | (1 << v(k, j))})
    for i in range(m):
        for j, k in itertools.combinations(range(n), 2):
            axioms.append({(1 << v(i, j)) | (1 << v(i, k))})
    axioms += [{0} | {1 << v(i, j) for j in range(n)} for i in range(m)]
    return axioms, m * n, v


def deg(m):
    return bin(m).count('1')


def top_parts(c, k):
    """A basis, as bit vectors over the degree-k monomials, of T_k: degree-k parts of rows with pivot of degree k."""
    monos = [m for m in c.monos if deg(m) == k]
    idx = {m: i for i, m in enumerate(monos)}
    basis = {}
    for p, row in c.rows.items():
        if deg(c.monos[p]) != k:
            continue
        v = 0
        for m in c.poly(row):
            if deg(m) == k:
                v ^= 1 << idx[m]
        add(basis, v)
    return monos, idx, basis


def add(basis, v):
    for p in sorted(basis, reverse=True):
        if v >> p & 1:
            v ^= basis[p]
    if v:
        p = v.bit_length() - 1
        for q in list(basis):
            if basis[q] >> p & 1:
                basis[q] ^= v
        basis[p] = v
        return True
    return False


def reduce(basis, v):
    for p in sorted(basis, reverse=True):
        if v >> p & 1:
            v ^= basis[p]
    return v


def beta_prime(c, errors, D):
    """Least a <= D - e with g in G_a \\ T_a and g * top(E) in T_(a+e) for all E (errors are monomial masks)."""
    e = max(deg(E) for E in errors)
    for a in range(0, D - e + 1):
        monos_a, idx_a, T_a = top_parts(c, a)
        # The linear map g -> (residue of g*E modulo T_(a+e_E)) for each E; its kernel, modulo T_a.
        targets = {}
        for E in errors:
            k = a + deg(E)
            targets[E] = top_parts(c, k)
        rows = []          # images of the basis monomials of G_a, concatenated over the errors
        for m in monos_a:
            image = 0
            shift = 0
            for E in errors:
                monos_k, idx_k, T_k = targets[E]
                v = 0
                if m & E == 0:
                    v = 1 << idx_k[m | E]
                image |= reduce(T_k, v) << shift
                shift += len(monos_k)
            rows.append(image)
        # Kernel of the map on G_a: combinations of monomials with zero image; then test against T_a.
        kernel = kernel_of(rows)
        for g in kernel:
            if reduce(T_a, g):
                return a
    return None


def kernel_of(rows):
    """A basis of {combinations of rows (as bit vectors over row indices) that sum to zero}."""
    pivots = {}
    kernel = []
    for i, r in enumerate(rows):
        tag = 1 << i
        for p in sorted(pivots, reverse=True):
            if r >> p & 1:
                r ^= pivots[p][0]
                tag ^= pivots[p][1]
        if r:
            pivots[r.bit_length() - 1] = (r, tag)
        else:
            kernel.append(tag)
    return kernel


def least_killer(c, errors, D):
    """Least k <= D - e with f in V_k, f not in C, f*E in C for every E."""
    e = max(deg(E) for E in errors)
    for k in range(0, D - e + 1):
        monos = [m for m in c.monos if deg(m) <= k]
        rows = []
        for m in monos:
            image = 0
            for t, E in enumerate(errors):
                image |= c.reduce(c.vector(pc.multiply({m}, {E}))) << (t * len(c.monos))
            rows.append(image)
        for tag in kernel_of(rows):
            f = set()
            for i in range(tag.bit_length()):
                if tag >> i & 1:
                    f ^= {monos[i]}
            if not c.contains(f):
                return k
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    m, n, D = 6, 5, 3
    axioms, nv, v = functional_php(m, n)
    c = pc.Closure(axioms, nv, D)
    assert c.proper, 'the 6 x 5 functional system must be proper at degree 3'
    x = lambda i, j: 1 << v(i, j)
    sets = {'x00': [x(0, 0)], 'x00,x11': [x(0, 0), x(1, 1)], 'x00,x10': [x(0, 0), x(1, 0)],
            'x00,x01': [x(0, 0), x(0, 1)], 'x00x11': [x(0, 0) | x(1, 1)], 'x00x11,x22x33': [x(0, 0) | x(1, 1), x(2, 2) | x(3, 3)]}
    out = {'system': 'functional pigeonhole, 6 pigeons, 5 holes, F_2, multilinear', 'D': D, 'closure_dim': c.dim,
           'sets': {}}
    for name, errors in sets.items():
        b, k = beta_prime(c, errors, D), least_killer(c, errors, D)
        assert b is not None and k is not None and b <= k, (name, b, k)
        out['sets'][name] = {'beta_prime': b, 'least_surviving_killer': k}
        print(name, 'beta_prime', b, 'least surviving killer', k, flush=True)
    # Control: the constant error 1 has no surviving killer.
    assert least_killer(c, [0], D) is None and beta_prime(c, [0], D) is None
    out['control_constant_error'] = 'no surviving killer, beta_prime undefined'
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')
    print('PASS', flush=True)


if __name__ == '__main__':
    main()
