"""The reviewer's exact value at K=2, L=1 (unverified suggestion): floor(a/2) + 1 functionals on F_2^a.

Setting as in native_upper.py: rows f -> sum_{x in S} f(x) v(x), v of degree <= 1, on f of degree <= 2 over
F_2^a; detection is rank N_a(2). Construction (the reviewer's): S_0 = B_1 (the origin and the unit vectors), and
for each part of a decomposition of the edges of K_a into connected spanning pieces (a = 2b: b Hamiltonian paths
i, i+1, i-1, i+2, i-2, ... mod 2b; a = 2b+1: b Hamiltonian cycles through a centre, Walecki's construction, each
odd), the set of weight-two points e_i + e_j of its edges. The script builds the decomposition and asserts that its
parts are edge-disjoint, cover K_a, and are each a spanning path or an odd spanning cycle.
Statement tested: with these floor(a/2) + 1 sets the rank is N_a(2), for a = 3..9; floor(a/2) + 1 is the lower
bound ceil(N_a(2)/(a+1)) of lem:native-detection-count (a), so the least number is exactly floor(a/2) + 1 there.
Expected: rank N_a(2) for a = 3..9.
Refuted by: a rank below N_a(2) for some a, which would refute the reviewer's argument.
Possible because: the argument (stars span the cut space, the total edge sum adds one dimension exactly for a
non-bipartite graph) was checked by hand only.
Control: at a = 5, replacing one Hamiltonian piece by an even cycle on four vertices (bipartite, not spanning)
must lower the rank by at least one, as the cut-space count predicts; asserted.
Refuted by: rank N_5(2) = 16 with the even cycle, which would contradict the cut-space count.
Possible because: if the edge-sum and star forms recovered more than the cut space plus parity, it would not drop.
Positive control: the construction itself at a = 3 and 4 equals or matches native_upper.py's explicit sets (rank 7
and 11), whose ranks were computed there; asserted.
Refuted by: a rank other than 7 or 11 at a = 3, 4.
Possible because: an error in the decomposition code.
Baseline: the ball-translate bound N_a(1) = a + 1 and the lower bound ceil(N_a(2)/(a+1)); the construction aims at
the lower bound.
Record checked: the claims read were lem:native-detection-count and lem:native-functional-growth; neither
gives an exact value.
"""
import argparse
import importlib.util
import json
import pathlib

spec = importlib.util.spec_from_file_location('native_upper', pathlib.Path(__file__).with_name('native_upper.py'))
nu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nu)


def edge(i, j):
    return frozenset((i, j))


def decomposition(a):
    if a % 2 == 0:
        b, parts = a // 2, []
        for i in range(b):
            order = [i]
            for k in range(1, a):
                order.append((i + (k + 1) // 2 * (1 if k % 2 else -1)) % a)
            parts.append([edge(order[t], order[t + 1]) for t in range(a - 1)])
        return parts
    b, c = (a - 1) // 2, a - 1          # vertices 0..a-2 on a circle of size 2b, centre c
    parts = []
    for i in range(b):
        order = [i]
        for k in range(1, 2 * b):
            order.append((i + (k + 1) // 2 * (1 if k % 2 else -1)) % (2 * b))
        cyc = [c] + order + [c]
        parts.append([edge(cyc[t], cyc[t + 1]) for t in range(len(cyc) - 1)])
    return parts


def check_parts(a, parts):
    seen = [e for p in parts for e in p]
    assert len(seen) == len(set(seen)) == a * (a - 1) // 2, 'edge-disjoint cover'
    for p in parts:
        verts = set().union(*p)
        assert len(verts) == a
        assert len(p) in (a - 1, a)
        if len(p) == a:
            assert a % 2 == 1, 'a cycle part is odd'


def sets(a, parts):
    unit = lambda i: 1 << i
    return [[0] + [unit(i) for i in range(a)]] + [[unit(i) | unit(j) for i, j in map(tuple, p)] for p in parts]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = {'cases': []}
    for a in range(3, 10):
        parts = decomposition(a)
        check_parts(a, parts)
        S = sets(a, parts)
        r = nu.rank(a, 2, 1, S)
        N2 = len(nu.monomials(a, 2))
        lower = -(-N2 // (a + 1))
        out['cases'].append({'a': a, 'functionals': len(S), 'rank': r, 'N_2': N2, 'lower_bound': lower})
        assert len(S) == a // 2 + 1 == lower
        if a in (3, 4):
            assert r == {3: 7, 4: 11}[a], 'positive control'
        assert r == N2, a
    parts = decomposition(5)
    four_cycle = [edge(0, 1), edge(1, 2), edge(2, 3), edge(3, 0)]
    S = sets(5, [four_cycle] + parts[1:])
    out['control_even_cycle_a5'] = nu.rank(5, 2, 1, S)
    assert out['control_even_cycle_a5'] < 16, 'control'
    print(json.dumps(out, indent=1), flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
