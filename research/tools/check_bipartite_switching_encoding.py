#!/usr/bin/env python3
"""Exact round-trip test of the encoding used in the bipartite matching switching lemma.

Board: pigeons 0..n, holes 0..n-1. A restriction is a partial matching mu of size n-l (residual
l+1 pigeons, l holes). F is an ordered list of terms (partial matchings) of size <= r. The canonical
matching decision tree T(F|mu) is built as in Beame's primer, Section 5, on the bipartite board.
For every mu whose tree has height >= s, the lexicographically first path pi of length >= s is
trimmed to s edges and encoded as (mu+sigma, beta, masks, delta'); the decoder must return mu.
The script counts bad restrictions, verifies the round trip and the size bookkeeping
s/2 <= |sigma| <= 2s, and compares the bad fraction with the lemma's bound when it is below one.
"""
import argparse, itertools, json, math, sys

def restrict_term(term, mu_set, matched_p, matched_h):
    """Return (falsified, free_edges) of a term under restriction mu."""
    free = []
    for (p, h) in term:
        if (p, h) in mu_set:
            continue                      # satisfied edge removed
        if p in matched_p or h in matched_h:
            return True, None             # edge set to zero
        free.append((p, h))
    return False, free

def first_surviving(F, mu):
    mu_set = set(mu); mp = {p for p, _ in mu}; mh = {h for _, h in mu}
    for idx, term in enumerate(F):
        fals, free = restrict_term(term, mu_set, mp, mh)
        if not fals:
            return idx, free
    return None, None

def vertices(edges):
    out = []
    for p, h in edges:
        out.append(('p', p)); out.append(('h', h))
    return out

def canonical_height(F, mu, n, l, cap):
    """Height of T(F|mu) and the lexicographically first path of length >= cap (or the longest path).
    Paths are lists of edges; branching order: holes/pigeons in increasing index."""
    best = {'h': 0, 'path': None}
    def rec(mu_cur, path):
        if best['path'] is not None:
            return
        idx, free = first_surviving(F, mu_cur)
        if idx is None or len(free) == 0:          # constant leaf
            best['h'] = max(best['h'], len(path)); 
            if len(path) >= cap and best['path'] is None: best['path'] = list(path)
            return
        K = []
        for (p, h) in free:                         # vertex order: term order, pigeon then hole
            K.append(('p', p)); K.append(('h', h))
        # complete tree for K: query vertices of K in order, skipping covered ones
        def complete(mu_cur, path, pos):
            if best['path'] is not None: return
            mp = {p for p, _ in mu_cur}; mh = {h for _, h in mu_cur}
            while pos < len(K) and ((K[pos][0] == 'p' and K[pos][1] in mp) or (K[pos][0] == 'h' and K[pos][1] in mh)):
                pos += 1
            if pos == len(K):
                rec(mu_cur, path); return
            side, v = K[pos]
            if side == 'p':
                partners = [h for h in range(n) if h not in mh]
                for h in partners:
                    complete(mu_cur + [(v, h)], path + [(v, h)], pos + 1)
                    if best['path'] is not None: return
            else:
                partners = [p for p in range(n + 1) if p not in mp]
                for p in partners:
                    complete(mu_cur + [(p, v)], path + [(p, v)], pos + 1)
                    if best['path'] is not None: return
        complete(mu_cur, path, 0)
    rec(list(mu), [])
    return best['h'], best['path']

def encode(F, mu, pi, r, n):
    """Return (mu_sigma, betas, masks, deltas) and j=|sigma|."""
    rounds = []                # list of (nu, sigma_i, pi_i)
    cur = list(mu); rest = list(pi)
    while rest:
        nu, free = first_surviving(F, cur)
        assert nu is not None and free
        K = set(vertices(free))
        # pi_i = edges of rest touching K (they are a prefix of rest by construction)
        pi_i = []
        for e in rest:
            if ('p', e[0]) in K or ('h', e[1]) in K:
                pi_i.append(e)
            else:
                break
        assert pi_i, "path edge does not touch the current term"
        assert all((('p', e[0]) in K or ('h', e[1]) in K) for e in rest[:len(pi_i)])
        touched = set(v for e in pi_i for v in (('p', e[0]), ('h', e[1])))
        sigma_i = [e for e in free if ('p', e[0]) in touched or ('h', e[1]) in touched]
        assert sigma_i
        rounds.append((nu, sigma_i, pi_i, free))
        cur = cur + pi_i; rest = rest[len(pi_i):]
    sigma = [e for _, s, _, _ in rounds for e in s]
    mu_sigma = sorted(set(mu) | set(sigma))
    assert len(mu_sigma) == len(mu) + len(sigma), "sigma not compatible with mu"
    betas = []; masks = []; deltas = []
    ms_p = {q for q, _ in mu_sigma}; ms_h = {g for _, g in mu_sigma}
    known_p = set(p for p in range(n + 1) if p not in ms_p); known_h = set(h for h in range(n) if h not in ms_h)
    for nu, sigma_i, pi_i, free in rounds:
        known_p |= {p for p, _ in sigma_i}; known_h |= {h for _, h in sigma_i}
        resid_p = sorted(known_p); resid_h = sorted(known_h)
        term = F[nu]
        betas.append(tuple(1 if e in sigma_i else 0 for e in term))
        vs = vertices(sigma_i)
        touched = set(v for e in pi_i for v in (('p', e[0]), ('h', e[1])))
        masks.append(tuple(1 if v in touched else 0 for v in vs))
        covered = set()
        for e in pi_i:
            # first endpoint: smallest-index touched, uncovered vertex of v(sigma_i) in the edge
            cand = [v for v in vs if v in touched and v not in covered]
            first = cand[0]
            assert first in (('p', e[0]), ('h', e[1])), "edge does not contain the next touched vertex"
            if first[0] == 'p':
                deltas.append(resid_h.index(e[1]))
            else:
                deltas.append(resid_p.index(e[0]))
            covered.add(('p', e[0])); covered.add(('h', e[1]))
    return (tuple(mu_sigma), tuple(betas), tuple(masks), tuple(deltas)), len(sigma)

def decode(F, code, s, n):
    mu_sigma, betas, masks, deltas = code
    cur = list(mu_sigma)          # rho pi_1..pi_{i-1} sigma_i..sigma_k
    pis = []; sigmas = []
    ms_p = {q for q, _ in mu_sigma}; ms_h = {g for _, g in mu_sigma}
    known_p = set(p for p in range(n + 1) if p not in ms_p); known_h = set(h for h in range(n) if h not in ms_h)
    # residual vertices of rho: unknown until the end, but partners are residual vertices of rho
    # = vertices unset by mu_sigma plus v(sigma); we recover the numbering incrementally.
    d = 0
    for i, beta in enumerate(betas):
        nu, _ = first_surviving(F, cur)
        term = F[nu]
        sigma_i = [e for e, b in zip(term, beta) if b]
        vs = vertices(sigma_i)
        mask = masks[i]
        touched = {v for v, m in zip(vs, mask) if m}
        # residual vertices of rho known so far: unset by cur, plus v(sigma_1..sigma_i) (already replaced by pi for earlier rounds)
        known_p |= {p for p, _ in sigma_i}; known_h |= {h for _, h in sigma_i}
        resid_p = sorted(known_p); resid_h = sorted(known_h)
        pi_i = []; covered = set()
        while True:
            cand = [v for v in vs if v in touched and v not in covered]
            if not cand or sum(len(p) for p in pis) + len(pi_i) == s:
                break
            first = cand[0]
            if first[0] == 'p':
                e = (first[1], resid_h[deltas[d]])
            else:
                e = (resid_p[deltas[d]], first[1])
            d += 1
            pi_i.append(e); covered.add(('p', e[0])); covered.add(('h', e[1]))
        cur = [e for e in cur if e not in sigma_i] + pi_i
        pis.append(pi_i); sigmas.append(sigma_i)
    pi = [e for p in pis for e in p]
    mu = [e for e in cur if e not in pi]
    return tuple(sorted(mu))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=5); ap.add_argument('--l', type=int, default=2)
    ap.add_argument('--r', type=int, default=2); ap.add_argument('--s', type=int, default=2)
    ap.add_argument('--terms', type=int, default=8); ap.add_argument('--seed', type=int, default=20260918)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    import random
    rng = random.Random(a.seed)
    n, l, r, s = a.n, a.l, a.r, a.s
    # random r-disjunction: terms are partial matchings of size 1..r
    F = []
    while len(F) < a.terms:
        size = rng.randint(1, r)
        ps = rng.sample(range(n + 1), size); hs = rng.sample(range(n), size)
        F.append(tuple(sorted(zip(ps, hs))))
    pigeons = range(n + 1); holes = range(n)
    total = 0; bad = 0; failures = 0; jrange_ok = True; heights = {}
    for P in itertools.combinations(pigeons, n - l):
        for H in itertools.permutations(holes, n - l):
            mu = tuple(sorted(zip(P, H)))
            total += 1
            h, path = canonical_height(F, mu, n, l, s)
            heights[h] = heights.get(h, 0) + 1
            if h >= s:
                bad += 1
                pi = path[:s]
                code, j = encode(F, mu, pi, r, n)
                if not (math.ceil(s / 2) <= j <= 2 * s): jrange_ok = False
                if decode(F, code, s, n) != mu:
                    failures += 1
    A = 4 * r * l * (l + 1) / ((n - l + 1) * math.log(2))
    bound = 2 * ((l + 1) * math.sqrt(A)) ** s if A <= 0.5 else None
    res = {'n': n, 'l': l, 'r': r, 's': s, 'terms': [list(t) for t in F], 'seed': a.seed,
           'restrictions': total, 'bad': bad, 'bad_fraction': bad / total, 'round_trip_failures': failures,
           'sigma_size_range_ok': jrange_ok, 'height_histogram': heights, 'A': A, 'bound': bound}
    with open(a.out, 'a') as f: f.write(json.dumps(res) + '\n')
    print(json.dumps({k: v for k, v in res.items() if k != 'terms'}))
    return 0 if failures == 0 and jrange_ok else 1

if __name__ == '__main__':
    sys.exit(main())
