"""Every nonempty subset P of F_3^2 is cut out by a pairwise coherent family of product constraints on a
basis (u, v) chosen among the four directions of the pencil.

Factors per form: 1, chi_a(u) = 1-(u-a)^2 (zero set u != a), u - a' (zero set u = a'). Pairwise coherence on a
shared form allows only equal factors, or chi_a against u - a' with a' != a, so a coherent family uses on each
form at most one indicator chi_a and at most one linear factor u - a' with a' != a. The zero set of a constraint
is the union of its factors' zero sets; P is the intersection over the family.  For every P the script records
one witness (basis, a, a', b, b', constraints).  Usage: python3 coherent_pencil_sets.py OUT.json
"""
import itertools, json, sys
pts = [(x, y) for x in range(3) for y in range(3)]
dirs = [(1, 0), (0, 1), (1, 1), (1, 2)]
val = lambda d, p: (d[0] * p[0] + d[1] * p[1]) % 3
def zero(f, d, p):
    t, k = f; v = val(d, p)
    return v != k if t == 'chi' else v == k
wit = {}
for du, dv in itertools.combinations(dirs, 2):
    for a in range(3):
        for a2 in [None] + [x for x in range(3) if x != a]:
            for b in range(3):
                for b2 in [None] + [x for x in range(3) if x != b]:
                    fu = [None, ('chi', a)] + ([('lin', a2)] if a2 is not None else [])
                    fv = [None, ('chi', b)] + ([('lin', b2)] if b2 is not None else [])
                    cons = [(x, y) for x in fu for y in fv if (x, y) != (None, None)]
                    for m in range(1, len(cons) + 1):
                        for S in itertools.combinations(cons, m):
                            P = frozenset(p for p in pts if all(
                                any(zero(f, d, p) for f, d in zip(c, (du, dv)) if f is not None) for c in S))
                            key = tuple(sorted(P))
                            if P and key not in wit:
                                wit[key] = dict(basis=[du, dv], constraints=[list(c) for c in S])
n_subsets = 2 ** 9 - 2                      # nonempty proper subsets; P = F_3^2 needs no constraint
print('proper nonempty subsets described:', len(wit) - (1 if tuple(sorted(pts)) in wit else 0), 'of', n_subsets)
assert all(tuple(sorted(P)) in wit for r in range(1, 9) for P in itertools.combinations(pts, r))
json.dump(dict(witnesses=[dict(P=list(k), **v) for k, v in sorted(wit.items())]), open(sys.argv[1], 'w'), indent=1)
