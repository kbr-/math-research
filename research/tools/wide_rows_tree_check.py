#!/usr/bin/env python3
"""Cycle 211: heights of the compact complete-term tree T_c(F, rho') on readers with wide tail rows, over every
rho' in Phi_0 for every two-hole or four-hole flat of F_2^L, with and without the static skip (a term with a
residual tail row whose pattern cube misses Q counts as falsified, i.e. the tree of the sub-reader F_{Q,R'}).

Readers (rows 0..n; A = pinned rows, B = the rest):
  same-pattern:  [j in p] for every j in B, one pattern p of L-1 literals (two labels), pin-free;
  distinct:      [j in p_j] for every j in B, p_j of L-1 literals with distinct cubes, pin-free;
  one-pin:       [i -> x] and [j in p] for every j in B, one pin (i, x), the same p as above.
For each flat Q and each rho' = (Q, R', mu') the script records the height of T_c (the longest path), the number of
residual rows of B, whether some term is satisfied by rho' at the root, and whether C(p) meets Q; it prints, per
reader and per skip mode, the fraction of rho' with height >= h for the thresholds h = 1, 2, 3, split by whether the
pattern cube meets the flat.  Usage: wide_rows_tree_check.py --L 3 --L2 1 --out FILE"""
import argparse, itertools, json, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_pair_space_encoding import first_long_path_compact, consistent

def flats(n, L, L2):
    """Every affine subspace of dimension L2 of F_2^L, as a sorted tuple of labels."""
    out = set()
    for vecs in itertools.combinations(range(1, n), L2):
        span = {0}
        for v in vecs: span |= {x ^ v for x in span}
        if len(span) != 2 ** L2: continue
        for tr in range(n): out.add(tuple(sorted(x ^ tr for x in span)))
    return sorted(out)

def readers(n, L, A, B):
    p = [(t, 0) for t in range(L - 1)]                   # cube {0, 2^(L-1)}: bits 0..L-2 zero
    same = [{'pin': None, 'tail': [(j, p)]} for j in B]
    dist = []
    for k, j in enumerate(B):                            # cube of j: bits 0..L-2 fixed to the binary digits of k
        dist.append({'pin': None, 'tail': [(j, [(t, (k >> t) & 1) for t in range(L - 1)])]})
    i0, x0 = A[0], 1                                     # pin (A[0], label 1); label 1 lies in no cube above? it lies in the cube of k=1 (distinct)
    onepin = [{'pin': (i0, x0), 'tail': [(j, p)]} for j in B]
    return {'same-pattern': same, 'distinct': dist, 'one-pin': onepin}

def static_skip(F, Rp, Qs):
    """The sub-reader F_{Q,R'}: terms without a residual tail row whose pattern cube misses Q."""
    keep = []
    for t in F:
        ok = True
        for row, lits in t['tail']:
            if row in Rp and not any(consistent(lits, q) for q in Qs): ok = False; break
        if ok: keep.append(t)
    return keep

def satisfied(F, mu):
    for t in F:
        if t['pin'] is not None and mu.get(t['pin'][0]) != t['pin'][1]: continue
        if all(row in mu and consistent(lits, mu[row]) for row, lits in t['tail']): return True
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--L', type=int, default=3); ap.add_argument('--L2', type=int, default=1)
    ap.add_argument('--pinned', type=int, default=3); ap.add_argument('--out', required=True)
    ap.add_argument('--max-flats', type=int, default=0)
    a = ap.parse_args()
    n = 2 ** a.L; N = 2 ** a.L2; rows = list(range(n + 1)); A = rows[:a.pinned]; B = rows[a.pinned:]
    R = readers(n, a.L, A, B); q = n + 1 - (N + 1)
    Fs = flats(n, a.L, a.L2)
    if a.max_flats: Fs = Fs[:a.max_flats]
    p_cube = {y for y in range(n) if all(((y >> t) & 1) == 0 for t in range(a.L - 1))}
    results = {}
    for name, F in R.items():
        for skip in (False, True):
            stats = {}
            for Q in Fs:
                Qs = set(Q); O = [y for y in range(n) if y not in Qs]; meets = bool(p_cube & Qs)
                key = f'meets={meets}'
                st = stats.setdefault(key, {'count': 0, 'h1': 0, 'h2': 0, 'h3': 0, 'hN8': 0, 'sat': 0, 'maxh': 0, 'sumRB': 0})
                for matched in itertools.combinations(rows, q):
                    Rp = [r for r in rows if r not in matched]
                    for labs in itertools.permutations(O, q):
                        mu = dict(zip(matched, labs))
                        st['count'] += 1; st['sumRB'] += sum(1 for r in Rp if r in B)
                        if satisfied(F, mu): st['sat'] += 1; continue
                        F2 = static_skip(F, Rp, Qs) if skip else F
                        res = first_long_path_compact(F2, mu, Rp, Q, 10 ** 6)
                        h = res['height']; st['maxh'] = max(st['maxh'], h)
                        for k in (1, 2, 3):
                            if h >= k: st[f'h{k}'] += 1
            results[f'{name}|skip={skip}'] = stats
            for key, st in stats.items():
                c = st['count']
                print(f"{name:13s} skip={skip!s:5s} {key:12s} rho'={c:7d} satisfied={st['sat']/c:.3f} h>=1:{st['h1']/c:.3f} h>=2:{st['h2']/c:.3f} h>=3:{st['h3']/c:.3f} max={st['maxh']} mean|R' n B|={st['sumRB']/c:.2f}")
    rec = {'L': a.L, 'L2': a.L2, 'n': n, 'N': N, 'pinned': a.pinned, 'flats': len(Fs), 'results': results}
    with open(a.out, 'a') as f: f.write(json.dumps(rec) + '\n')

if __name__ == '__main__':
    main()
