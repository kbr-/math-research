#!/usr/bin/env python3
"""Matching-complex filling on twin-hole boards against random boards of the same degrees.

Tested statement (26 September 2026): the hypothesis of lem:graph-matching-extension,
H~_{|S|-2}(M(G[S]); F_3) = 0 for row sets S, fails on random sparse boards at spider row sets
(prop:spider-unfilled). A twin-hole board (every hole of a random bipartite graph doubled, so holes
come in pairs with equal pigeon sets) has no spiders, since every pigeon at a hole of r is also at
its twin. Question: is M(G[S]) filled in degree |S|-2 on twin boards for overlapping row sets S,
while the random control is not?
Boards: twin board from P pigeons, Q original holes, each pigeon a uniform d-subset (pigeon degree
2d after doubling); control: P pigeons, 2Q holes, each pigeon a uniform 2d-subset. Row sets are
grown connected (each new row shares a hole with the set). Reports, per board type and |S|, the
number of sampled row sets with nonzero reduced homology in degree |S|-2.
Exact ranks over F_3 by the FLINT helper of matching_complex.py (pass RANK_BIN).
Usage: twin_filling.py --out PATH [--P 121] [--Q 60] [--d 2] [--smax 6] [--samples 40] [--seed S]
"""
import argparse, json, sys
import numpy as np
sys.path.insert(0, '/home/kbr/dev/math-auxiliary/research/results/odd_prime_expander_extension_20260926')
from matching_complex import reduced_homology


def twin_board(rng, P, Q, d):
    base = [rng.choice(Q, size=d, replace=False).tolist() for _ in range(P)]
    return [frozenset([2 * t for t in b] + [2 * t + 1 for t in b]) for b in base]


def random_board(rng, P, H, deg):
    return [frozenset(rng.choice(H, size=deg, replace=False).tolist()) for _ in range(P)]


def grow(rng, nbrs, s):
    S = [int(rng.integers(len(nbrs)))]
    while len(S) < s:
        holes = set().union(*(nbrs[i] for i in S))
        cand = [i for i in range(len(nbrs)) if i not in S and nbrs[i] & holes]
        if not cand:
            return None
        S.append(int(rng.choice(cand)))
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--P', type=int, default=121)
    ap.add_argument('--Q', type=int, default=60)
    ap.add_argument('--d', type=int, default=2)
    ap.add_argument('--smax', type=int, default=6)
    ap.add_argument('--samples', type=int, default=40)
    ap.add_argument('--seed', type=int, default=20260926)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    boards = {'twin': twin_board(rng, a.P, a.Q, a.d),
              'random_control': random_board(rng, a.P, 2 * a.Q, 2 * a.d)}
    res = {'params': vars(a), 'rows': []}
    for name, nbrs in boards.items():
        for s in range(2, a.smax + 1):
            tested = nonzero = 0
            examples = []
            while tested < a.samples:
                S = grow(rng, nbrs, s)
                if S is None:
                    continue
                tested += 1
                sub = [nbrs[i] for i in S]
                if reduced_homology(sub, s - 2) != 0:
                    nonzero += 1
                    if len(examples) < 2:
                        examples.append([sorted(x) for x in sub])
            row = {'board': name, 's': s, 'tested': tested, 'nonzero': nonzero, 'examples': examples}
            res['rows'].append(row)
            print(json.dumps({k: row[k] for k in ('board', 's', 'tested', 'nonzero')}), flush=True)
    json.dump(res, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
