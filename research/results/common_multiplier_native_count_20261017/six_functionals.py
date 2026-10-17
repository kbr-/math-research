"""Six native functionals at the top degree of the product pigeonhole system (5 pigeons, 4 holes, E = x_00).

Statement tested (prop:top-degree-native-count, its instance part, entry-2026-10-17-top-degree-native): on the
error's support S_E = {0..5}^3 (three free holes, each empty or holding one of five pigeons), with u of degree
<= 2 (91 coefficients) and v of degree <= 1 (16 monomials), six functionals detect the kernel: the ball sum nu_0
over the 16 points with at most one nonempty free hole, and for each piece G of a decomposition of the 75 edges
of K_{5,5,5} into five spanning graphs, the sum nu_G over the weight-two points of G's edges. Detection means the
96 forms (nu, v) -> sum_z nu(z) v(z) u(z), as rows on the 91 coefficients, have rank 91. With the lower bound
ceil(91/16) = 6 of lem:native-detection-count (a), rank 91 gives m_min = 6.

Decompositions, vertices t in Z_15 with hole t mod 3 and pigeon t // 3: the circulant one, difference classes
+-1, +-2, +-4, +-7 (Hamiltonian 15-cycles) and +-5 (five triangles); and a repaired one, in which classes +-1 and
+-5 are replaced by two edge-disjoint Hamiltonian cycles of their union, found here by search.
Expected (the reviewer's unverified argument, with the unsigned incidence kernel E - V + bipartite components
in characteristic other than 2, and the cycle space with the total sum over F_2): the circulant rank 91 over F_3
and F_5 and 87 over F_2 (the triangles' piece of rank 11); the repaired decomposition rank 91 over F_2, F_3, F_5.
Refuted by: a printed rank other than 91 for the repaired decomposition over F_2, or for the circulant over F_3.
Possible because: the reduction to star sums and the total sum could miss a dependence among the forms.
Control: the circulant decomposition over F_2, expected rank 87, below 91, so the rank computation can fail.
Positive control: the ball sum nu_0 alone has rank 16, the coefficients of degree at most one, asserted.
Forced by counts: 96 rows against 91 columns, so rank 91 is not forced; the F_2 control's rank 87 is below it.
Baseline: point evaluations on the 91 points with at most two nonempty free holes give rank 91 with 91
functionals; the ball sums of lem:native-rectangle-upper-bound's construction give 16; the lower bound is 6.
Record checked: lem:native-detection-count, lem:native-rectangle-upper-bound and check:native-upper-ranks (the
cube's exact floor(a/2)+1 by a cut-space construction); none gives the count on {0..5}^3.
"""
import itertools
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
from f2_span import Span   # noqa: E402

HOLES, PIGEONS = 3, 5
POINTS = list(itertools.product(range(PIGEONS + 1), repeat=HOLES))
LIN = [(h, i) for h in range(HOLES) for i in range(1, PIGEONS + 1)]
MONOS = [()] + [(a,) for a in LIN] + [(a, b) for a, b in itertools.combinations(LIN, 2) if a[0] != b[0]]
VMONOS = [()] + [(a,) for a in LIN]
assert len(MONOS) == 91 and len(VMONOS) == 16


def value(mono, z):
    return int(all(z[h] == i for h, i in mono))


def vertex(t):
    return (t % 3, t // 3 + 1)


def point_of_edge(a, b):
    z = [0] * HOLES
    z[a[0]], z[b[0]] = a[1], b[1]
    return tuple(z)


def circulant(d):
    return [frozenset((vertex(t), vertex((t + d) % 15))) for t in range(15)]


def is_hamiltonian(edges):
    adj = {}
    for e in edges:
        a, b = tuple(e)
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    if len(adj) != 15 or any(len(v) != 2 for v in adj.values()):
        return False
    start, prev, cur, n = next(iter(adj)), None, None, 1
    prev, cur = start, adj[start][0]
    while cur != start:
        nxt = adj[cur][0] if adj[cur][0] != prev else adj[cur][1]
        prev, cur, n = cur, nxt, n + 1
    return n == 15


def split_into_two_cycles(edges, seed=1):
    """Two edge-disjoint Hamiltonian cycles covering a 4-regular graph, by randomized search."""
    rng = random.Random(seed)
    edges = list(edges)
    adj = {}
    for e in edges:
        a, b = tuple(e)
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    verts = sorted(adj)
    for _ in range(200000):
        start = verts[0]
        path, used = [start], {start}
        while len(path) < 15:
            options = [w for w in adj[path[-1]] if w not in used]
            if not options:
                break
            w = rng.choice(options)
            path.append(w)
            used.add(w)
        if len(path) < 15 or start not in adj[path[-1]]:
            continue
        cycle = {frozenset((path[k], path[(k + 1) % 15])) for k in range(15)}
        rest = [e for e in edges if e not in cycle]
        if is_hamiltonian(rest):
            return sorted(cycle, key=sorted), sorted(rest, key=sorted)
    raise RuntimeError('no split found')


def rows(functionals):
    out = []
    for nu in functionals:
        for v in VMONOS:
            out.append([sum(w * value(v, z) * value(s, z) for z, w in nu.items()) for s in MONOS])
    return out


def rank_mod(m, p):
    if p == 2:
        span = Span()
        for r in m:
            span.add(sum((x % 2) << k for k, x in enumerate(r)))
        return len(span)
    m = [[x % p for x in r] for r in m]
    rk, cols = 0, len(m[0])
    for c in range(cols):
        piv = next((i for i in range(rk, len(m)) if m[i][c]), None)
        if piv is None:
            continue
        m[rk], m[piv] = m[piv], m[rk]
        inv = pow(m[rk][c], p - 2, p)
        m[rk] = [x * inv % p for x in m[rk]]
        for i in range(len(m)):
            if i != rk and m[i][c]:
                f = m[i][c]
                m[i] = [(x - f * y) % p for x, y in zip(m[i], m[rk])]
        rk += 1
    return rk


def main(out):
    nu0 = {z: 1 for z in POINTS if sum(1 for x in z if x) <= 1}
    assert len(nu0) == 16
    assert rank_mod(rows([nu0]), 3) == 16 and rank_mod(rows([nu0]), 2) == 16      # positive control
    classes = {d: circulant(d) for d in (1, 2, 4, 7, 5)}
    all_edges = set().union(*classes.values())
    assert len(all_edges) == 75 and all(len(set(c)) == 15 for c in classes.values())
    assert all(is_hamiltonian(classes[d]) for d in (1, 2, 4, 7)) and not is_hamiltonian(classes[5])
    h1, h2 = split_into_two_cycles(classes[1] + classes[5])
    repaired = [classes[2], classes[4], classes[7], h1, h2]
    assert set().union(*map(set, repaired)) == all_edges and all(is_hamiltonian(g) for g in repaired)

    def functionals(pieces):
        return [nu0] + [{point_of_edge(*tuple(e)): 1 for e in g} for g in pieces]

    result = {'circulant': {}, 'repaired': {}, 'repaired_cycles': [[sorted(e) for e in h1], [sorted(e) for e in h2]]}
    for name, pieces in (('circulant', [classes[d] for d in (1, 2, 4, 7, 5)]), ('repaired', repaired)):
        m = rows(functionals(pieces))
        assert len(m) == 96
        for p in (2, 3, 5):
            result[name][str(p)] = rank_mod(m, p)
            print(name, 'p =', p, 'rank', result[name][str(p)], 'of 91 with 6 functionals', flush=True)
    json.dump(result, open(out, 'w'), indent=1)
    assert result['circulant']['2'] < 91                               # control: the rank can fall short
    ok = result['repaired'] == {'2': 91, '3': 91, '5': 91} and result['circulant']['3'] == 91
    print('PASS' if ok else 'FAIL')


if __name__ == '__main__':
    main(sys.argv[sys.argv.index('--out') + 1])
