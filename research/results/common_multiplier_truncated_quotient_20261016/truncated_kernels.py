"""Do degree-truncated PC quotients give error kernels beyond support kernels plus relations?

Statement tested (hypothesis for entry-2026-10-16-truncated-quotient): for an unsatisfiable multilinear
system F over F_2, its degree-D PC closure C_D (1 not in C_D), B_D the multilinear polynomials of degree
<= D vanishing on the cube (in the multilinear ring: zero), and Pang-form errors E = P g (P = 1 + q,
q in the family's input span, deg E + K <= D), the kernel ker_C(E) = {u in V_K : E u in C_D} equals
ker_B(E) + (C_D cap V_K), where ker_B(E) = {u : E u = 0 as a function} (support kernel). Equality says
every proper-quotient kernel element is a support-kernel element plus a relation, so joint savings in the
proper quotient are support savings; a strict inclusion is a truncation effect.
Expected: unknown; the run decides at PHP^{m}_{m-1}, m = 3, 4, at the largest D with 1 not in C_D.
Refuted by: some error (or the stacked family) with dim ker_C larger than dim(ker_B + C_D cap V_K).
Possible because: C_D contains consequences such as E u for u outside the support kernel, which only
the unsatisfiable axioms supply.
Containment control: ker_B + relations inside ker_C, asserted for every case.
Refuted by: an assertion failure, which would mean the closure or the remainder is wrong.
Possible because: the first version of this script had a non-canonical remainder.
Control: with the empty system (only Booleanity, here built into the multilinear ring) C_D = 0 and the
two sides must be equal; the script asserts it.
Refuted by: unequal sides on the empty system, which would mean the kernel computation is wrong.
Possible because: an indexing error in the monomial basis would break the control.
"""
import argparse
import itertools
import json


def mono_index(nvars, dmax):
    monos = [m for k in range(dmax, -1, -1) for m in sorted(
        (sum(1 << i for i in c) for c in itertools.combinations(range(nvars), k)), reverse=True)]
    return monos, {m: i for i, m in enumerate(monos)}


def poly_vec(poly, index):
    v = 0
    for m in poly:
        v ^= 1 << index[m]
    return v


def mul_var(poly, var):
    out = {}
    for m in poly:
        t = m | (1 << var)
        out[t] = out.get(t, 0) ^ 1
    return {m for m, c in out.items() if c}


def mul(p, q):
    out = {}
    for a in p:
        for b in q:
            t = a | b
            out[t] = out.get(t, 0) ^ 1
    return {m for m, c in out.items() if c}


def deg(poly):
    return max((bin(m).count('1') for m in poly), default=-1)


class Space:
    """F_2 row space over the monomial basis (bit i = monomial i, degree-descending), pivot = lowest bit."""

    def __init__(self):
        self.rows = {}

    def reduce(self, v):
        """Canonical remainder: no pivot position stays set.  A row's lowest bit is its pivot, so
        eliminating pivots in ascending order only changes higher bits; the map is linear."""
        for p in sorted(self.rows):
            if v >> p & 1:
                v ^= self.rows[p]
        return v

    def add(self, v):
        v = self.reduce(v)
        if v:
            self.rows[(v & -v).bit_length() - 1] = v
            return True
        return False

    def dim(self):
        return len(self.rows)


def closure(axioms, nvars, D):
    """Degree-D PC closure in the multilinear ring.  Members of degree below D are spanned by the echelon
    rows whose pivot (their leading monomial, monomials being ordered by degree descending) has degree
    below D, so each pass multiplies every such row by every variable, until nothing new enters."""
    monos, index = mono_index(nvars, D)
    space = Space()
    for a in axioms:
        if deg(a) <= D:
            space.add(poly_vec(a, index))
    done = set()
    while True:
        todo = [p for p in space.rows if p not in done and bin(monos[p]).count('1') < D]
        if not todo:
            break
        for p in todo:
            done.add(p)
            row = space.rows.get(p)
            if row is None:
                continue
            poly = {monos[i] for i in range(row.bit_length()) if row >> i & 1}
            for x in range(nvars):
                q = mul_var(poly, x)
                if q:
                    space.add(poly_vec(q, index))
        # Rows can change when later additions are reduced; recheck every low pivot once more.
        if not any(p not in done for p in space.rows if bin(monos[p]).count('1') < D):
            changed = False
            for p in list(space.rows):
                if bin(monos[p]).count('1') < D:
                    row = space.rows[p]
                    poly = {monos[i] for i in range(row.bit_length()) if row >> i & 1}
                    for x in range(nvars):
                        q = mul_var(poly, x)
                        if q and space.add(poly_vec(q, index)):
                            changed = True
            if not changed:
                break
    one = space.reduce(poly_vec({0}, index)) == 0
    return space, monos, index, one


def php(m, n):
    var = lambda i, j: i * n + j
    axioms = []
    for i in range(m):
        p = {0}
        for j in range(n):
            p = mul(p, {0, 1 << var(i, j)})
        axioms.append(p)
    for j in range(n):
        for i, k in itertools.combinations(range(m), 2):
            axioms.append({(1 << var(i, j)) | (1 << var(k, j))})
    return axioms, m * n


def evaluate(poly, point):
    return sum(1 for mono in poly if mono & point == mono) % 2


def kernel_dims(errors, space, index, monos, nvars, K, D):
    """dim ker_C, dim (ker_B + C cap V_K), dim (C cap V_K) on V_K, for the stacked errors."""
    basis = [m for m in monos if bin(m).count('1') <= K]
    points = range(1 << nvars)
    # ker_C: u = sum c_b b with all E u in C_D; solve as kernel of the stacked reduction map.
    cols = []
    for b in basis:
        img = []
        for E in errors:
            img.append(space.reduce(poly_vec(mul(E, {b}), index)))
        cols.append(img)
    def kernel_of(columns):
        # columns: list of tuples of ints (one int per error); kernel by elimination on combined vectors
        width = max((v.bit_length() for col in columns for v in col), default=0) + 1
        vecs = []
        for i, col in enumerate(columns):
            combined = 0
            for e, v in enumerate(col):
                combined |= v << (e * width)
            vecs.append((combined, 1 << i))
        pivots = {}
        kern = []
        for combined, tag in vecs:
            while combined:
                p = combined.bit_length() - 1
                if p not in pivots:
                    pivots[p] = (combined, tag)
                    break
                combined ^= pivots[p][0]
                tag ^= pivots[p][1]
            if not combined:
                kern.append(tag)
        return kern
    ker_c = kernel_of(cols)
    # ker_B: u vanishing (as a function) on the union of the errors' supports.
    support = [x for x in points if any(evaluate(E, x) for E in errors)]
    bcols = [[sum(evaluate({b}, x) << i for i, x in enumerate(support))] for b in basis]
    ker_b = kernel_of(bcols)
    # C cap V_K: elements of V_K reducing to zero modulo C_D.
    rcols = [[space.reduce(poly_vec({b}, index))] for b in basis]
    ker_rel = kernel_of(rcols)
    span = Space()
    for t in ker_b + ker_rel:
        span.add(t)
    # Containment control: support kernel and relations lie in the proper kernel by construction.
    cspan = Space()
    for t in ker_c:
        cspan.add(t)
    assert all(cspan.reduce(t) == 0 for t in ker_b + ker_rel), 'ker_B + relations must lie in ker_C'
    return len(ker_c), span.dim(), len(ker_rel), len(basis)


def run_case(label, axioms, nvars, D, K, families):
    space, monos, index, one = closure(axioms, nvars, D)
    assert not one, 'the closure must be proper'
    errors = []
    rows = []
    for fam in families:
        q = set()
        for g in fam:
            q ^= g
        P = q ^ {0}
        fam_err = [mul(P, g) for g in fam]
        assert all(deg(E) + K <= D for E in fam_err)
        errors.extend(fam_err)
        kc, kbr, rel, dimv = kernel_dims(fam_err, space, index, monos, nvars, K, D)
        rows.append(dict(family=[sorted(g) for g in fam], ker_C=kc, ker_B_plus_rel=kbr))
    kc, kbr, rel, dimv = kernel_dims(errors, space, index, monos, nvars, K, D)
    return dict(case=label, nvars=nvars, D=D, K=K, dim_VK=dimv, relations_in_VK=rel,
                stacked_ker_C=kc, stacked_ker_B_plus_rel=kbr, families=rows,
                truncation_effect=kc > kbr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    results = []
    # Control: empty system on 6 variables.
    x = lambda i: {1 << i}
    ctrl = run_case('control-empty', [], 6, 3, 1, [[x(0), x(1)], [x(2), x(3)]])
    assert ctrl['stacked_ker_C'] == ctrl['stacked_ker_B_plus_rel'], 'control must agree'
    results.append(ctrl)
    for m in (3, 4):
        axioms, nvars = php(m, m - 1)
        D = None
        for d in range(2, 7):
            if not closure(axioms, nvars, d)[3]:
                D = d
            else:
                break
        print('PHP', m, 'largest proper D', D, flush=True)
        if D is None or D < 3:
            results.append(dict(case=f'php{m}', largest_proper_D=D, skipped='no proper D >= 3'))
            continue
        K = D - 2
        fams = [[x(a), x(b)] for a, b in itertools.combinations(range(nvars), 2)][:6]
        results.append(run_case(f'php{m}', axioms, nvars, D, K, fams))
    for r in results:
        print(json.dumps(r))
    with open(args.out, 'w') as handle:
        json.dump(results, handle, indent=1)
    print('PASS')


if __name__ == '__main__':
    main()
