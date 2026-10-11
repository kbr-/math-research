"""Least vanishing degree of a weight class modulo three, and the refutation degree of two such classes.

Statements tested (queue check entry-2026-10-10-occurrence-review:s1, its restated remaining parts).
C_a = points of {0,1}^n of weight congruent to a modulo 3; I_a = multilinear polynomials over F_2 vanishing on
C_a.  (1) d0(a) = least degree of a nonzero element of I_a.  The entry proves d0(a) <= c_a(n), the number of
weights w <= n congruent to a, by a symmetric polynomial; the computation gives the exact value, which could be
lower (an annihilator that is not symmetric) or equal.  (2) For a != b, the polynomial-calculus refutation
degree over F_2 of the system "x in C_a and x in C_b", each row given by all polynomials vanishing on its
class: the least D with 1 in the degree-D closure of (I_a)_{<=D} + (I_b)_{<=D}.  It is at least
max(d0(a), d0(b)); it is compared with n/3 and n/2.

Method.  The evaluation vector of a monomial on C_a is the AND of its variables' vectors.  Monomials are
processed by increasing degree and eliminated; each dependency is an element of I_a whose leading monomial is
the current one, so the elements with leaders of degree <= D are a basis of (I_a)_{<=D}.  Degrees of the
two-row system by tools/f2_closure_degree.cpp, compiled into a scratch directory.  Exact.  One-off job.

Usage: python3 weight_classes.py KERNEL_BINARY SCRATCH_DIR OUT.json
"""
import json
import subprocess
import sys


def ideal_basis(n, residue, dmax):
    """A basis of the polynomials of degree <= dmax vanishing on C_residue: lists of monomial masks."""
    points = [x for x in range(1 << n) if bin(x).count('1') % 3 == residue]
    variable = [sum(1 << j for j, x in enumerate(points) if x >> i & 1) for i in range(n)]
    everything = (1 << len(points)) - 1
    monos = sorted((t for t in range(1 << n) if bin(t).count('1') <= dmax), key=lambda t: (bin(t).count('1'), t))
    evaluation = {0: everything}
    pivots, basis = {}, []
    for position, t in enumerate(monos):
        if t:
            low = t & -t
            evaluation[t] = evaluation[t ^ low] & variable[low.bit_length() - 1]
        vector, combination = evaluation[t], 1 << position
        while vector:
            p = vector & -vector
            if p not in pivots:
                pivots[p] = (vector, combination)
                break
            other, other_combination = pivots[p]
            vector ^= other
            combination ^= other_combination
        else:
            basis.append([monos[i] for i in range(position + 1) if combination >> i & 1])
    return basis


def degree_of(poly):
    return max(bin(t).count('1') for t in poly)


def refutation_degree(binary, scratch, n, rows, dmax):
    path = f'{scratch}/classes.txt'
    with open(path, 'w') as handle:
        handle.write(f'{n} {len(rows)}\n')
        for r in rows:
            handle.write(f'{len(r)} ' + ' '.join(map(str, r)) + '\n')
    return json.loads(subprocess.run([binary, path, str(dmax)], check=True, capture_output=True, text=True).stdout)


def in_span(vectors, target):
    pivots = {}
    for v in vectors:
        while v:
            p = v & -v
            if p not in pivots:
                pivots[p] = v
                break
            v ^= pivots[p]
    while target:
        p = target & -target
        if p not in pivots:
            return False
        target ^= pivots[p]
    return True


def static_degree(n, first, second):
    """Least D with 1 = f + g, f and g of degree <= D vanishing on the first and the second class."""
    for d in range(n + 1):
        vectors = [sum(1 << t for t in p) for p in first + second if degree_of(p) <= d]
        if in_span(vectors, 1):                           # the constant is the monomial with mask 0
            return d
    return None


def hull_degree(n, first, second):
    """Least D at which the polynomials of degree <= D vanishing on the first class and those vanishing on the
    second have no common zero.  Below it the axioms of degree <= D are satisfiable together, so a refutation
    of degree D does not exist: a lower bound on the refutation degree that comes from the axioms' degrees."""
    variable = [sum(1 << x for x in range(1 << n) if x >> i & 1) for i in range(n)]
    value = {0: (1 << (1 << n)) - 1}
    for t in range(1, 1 << n):
        low = t & -t
        value[t] = value[t ^ low] & variable[low.bit_length() - 1]
    tables = []
    for basis in (first, second):
        rows = []
        for p in basis:
            v = 0
            for t in p:
                v ^= value[t]
            rows.append((degree_of(p), v))
        tables.append(sorted(rows))
    zeros = [value[0], value[0]]
    position = [0, 0]
    for d in range(n + 1):
        for k in (0, 1):
            while position[k] < len(tables[k]) and tables[k][position[k]][0] <= d:
                zeros[k] &= ~tables[k][position[k]][1]
                position[k] += 1
        if zeros[0] & zeros[1] == 0:
            return d
    return None


def odd_binomial(top, bottom):
    return 0 <= bottom <= top and (bottom & (top - bottom)) == 0


def layer_bound(n, a, b):
    """Largest D for which a sum of layer functionals of class a agrees through degree D with one of class b
    and is odd on the constant; -1 if none.  The layer functional of weight w sends a monomial of degree s to
    C(n-s, w-s) mod 2, the number of points of weight w above an s-set."""
    best = -1
    for d in range(n + 1):
        columns = [(sum(1 << s for s in range(d + 1) if odd_binomial(n - s, w - s)),
                    1 if w % 3 == a and odd_binomial(n, w) else 0)
                   for w in range(n + 1) if w % 3 in (a, b)]
        pivots, found = {}, False
        for vector, parity in columns:
            while vector:
                p = vector & -vector
                if p not in pivots:
                    pivots[p] = (vector, parity)
                    break
                other, other_parity = pivots[p]
                vector ^= other
                parity ^= other_parity
            else:
                found = found or parity == 1              # a dependency whose class-a part is odd on 1
        if not found:
            break
        best = d
    return best


def main(binary, scratch, out):
    results = []
    for n in range(4, 13):
        bases = [ideal_basis(n, a, n) for a in range(3)]
        least = [min(degree_of(p) for p in basis) for basis in bases]
        counts = [len([w for w in range(n + 1) if w % 3 == a]) for a in range(3)]
        pairs, static, layers, hulls = {}, {}, {}, {}
        for a, b in ((0, 1), (0, 2), (1, 2)):
            found = refutation_degree(binary, scratch, n, bases[a] + bases[b], n)
            pairs[f'{a},{b}'] = found['degree']
            static[f'{a},{b}'] = static_degree(n, bases[a], bases[b])
            layers[f'{a},{b}'] = max(layer_bound(n, a, b), layer_bound(n, b, a)) + 1
            hulls[f'{a},{b}'] = hull_degree(n, bases[a], bases[b])
        results.append({'n': n, 'least_vanishing_degree': least, 'weights_in_class': counts,
                        'refutation_degree': pairs, 'static_degree': static, 'hull_degree': hulls,
                        'layer_lower_bound_on_static': layers, 'third': round(n / 3, 2), 'half': n / 2})
        with open(out, 'w') as handle:
            json.dump({'small': results}, handle, indent=1)
    large = [{'n': n, 'layer_lower_bound_on_static': {
        f'{a},{b}': max(layer_bound(n, a, b), layer_bound(n, b, a)) + 1 for a, b in ((0, 1), (0, 2), (1, 2))}}
        for n in (15, 16, 17, 24, 31, 32, 33, 48, 63, 64, 65, 96, 100, 127, 128, 129, 200, 255, 256)]
    with open(out, 'w') as handle:
        json.dump({'small': results, 'large': large}, handle, indent=1)
    print(len(results), 'small sizes and', len(large), 'large sizes written')


if __name__ == '__main__':
    main(*sys.argv[1:4])
