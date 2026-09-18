#!/usr/bin/env python3
"""Counterexample to the distinct-holes claim of the adaptive heavy-query rule.

Full-column reader with k classes whose labels lie in the flat Q (|Q| = N), all tails satisfied by the
restriction, and all residual rows pinned.  Under the adaptive rule (pigeon query while the pinned row has
at least two unkilled pairs) the canonical tree has a path with about N-k+1 pigeon queries triggered by the
same hole; under the hole-only rule every path has at most k heavy queries.  Uses the tree of
check_mixed_term_encoding.py on one explicit restriction and reports the maximum heavy count over all paths.
"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_mixed_term_encoding as T

def build(L, L2, k):
    n = 2 ** L; N = 2 ** L2
    Q = list(range(N))                      # the subcube of labels with the top L-L2 bits zero
    rows = list(range(n + 1))
    light = list(range(k))                  # light rows 0..k-1, one per class
    pinned = [r for r in rows if r >= k]    # every other row is pinned
    R = set(pinned[:N + 1])                 # the N+1 residual rows are pinned rows
    matched = [r for r in rows if r not in R]
    outside = list(range(N, n))
    mu = {r: outside[t] for t, r in enumerate(matched)}   # light row j -> outside label N+j (tails below)
    F = []
    for c in range(k):
        x = Q[c]
        # tail: row c carries the pattern "label has the top L-L2 bits of its matched label", satisfied by mu
        lab = mu[c]; lits = [(t, (lab >> t) & 1) for t in range(L2, L)]
        for i in pinned:
            F.append({'pin': (i, x), 'tail': [(c, lits)]})
    return n, N, Q, R, mu, F

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--L', type=int, default=4); ap.add_argument('--L2', type=int, default=3)
    ap.add_argument('--classes', type=int, default=3); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    n, N, Q, R, mu, F = build(a.L, a.L2, a.classes)
    holes_all = sorted(Q)
    out = {'L': a.L, 'L2': a.L2, 'n': n, 'N': N, 'classes': a.classes, 'residual_rows': sorted(R),
           'labels_in_Q': Q[:a.classes], 'terms': len(F)}
    for hole_only in (False, True):
        T.HOLE_ONLY = hole_only
        res = T.first_long_path(F, mu, R, holes_all, 10 ** 6)
        out['hole_only' if hole_only else 'adaptive'] = {'max_heavy_queries': res['heavy'], 'max_height': res['height']}
    with open(a.out, 'w') as f: json.dump(out, f, indent=1)
    print(json.dumps(out))
    return 0

if __name__ == '__main__':
    sys.exit(main())
