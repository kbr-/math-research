#!/usr/bin/env python3
"""Exact round-trip test of the encoding for the slack-subcube bit switching lemma.

Labels are 0..n-1 with n = 2^L; residual labels are 0..N-1 (N = 2^L2, low bits free, high bits zero).
Family Phi_e: choose the residual pigeon set R of size N+1+e among n+1 pigeons and an injection mu of the
other pigeons into the outside labels O = N..n-1 (e outside labels stay free).  A reader F is an ordered
list of bit terms; a term is a dict row -> list of (bit, value) literals.  The canonical matching tree of
the residual instance (pigeons R, holes [N] plus the e free outside labels) queries the rows of the first
surviving term in order and branches over the available holes; a row with no available hole is a leaf.
For every restriction with a path of length >= s whose free labels are rich enough (the encoder finds a
consistent free outside label for every moved row), the trimmed lexicographically first long path is
encoded as (code restriction in Phi_{e-s}, star vectors beta, delta in (holes)^s) and decoded back.
"""
import argparse, itertools, json, math, random, sys

def bit(label, t): return (label >> t) & 1

def term_status(term, assign):
    """assign: row -> label (or absent). Returns ('false', None), ('true', None) or ('free', rows)."""
    free = []
    for row, lits in term.items():
        if row in assign:
            lab = assign[row]
            if any(bit(lab, t) != v for t, v in lits):
                return 'false', None
        else:
            free.append(row)
    return ('true', None) if not free else ('free', free)

def first_surviving(F, assign):
    for idx, term in enumerate(F):
        st, rows = term_status(term, assign)
        if st != 'false':
            return idx, st, rows
    return None, None, None

def canonical_path(F, assign, residual_labels, s):
    """Returns (height, lexicographically first path of length >= s as list of (row,label)) or (height, None)."""
    best = {'h': 0, 'path': None}
    def rec(assign, path):
        if best['path'] is not None: return
        idx, st, rows = first_surviving(F, assign)
        if idx is None or st == 'true':
            best['h'] = max(best['h'], len(path))
            if len(path) >= s: best['path'] = list(path)
            return
        def complete(assign, path, pos):
            if best['path'] is not None: return
            while pos < len(rows) and rows[pos] in assign: pos += 1
            if pos == len(rows):
                rec(assign, path); return
            row = rows[pos]
            used = set(assign[r] for r in assign if assign[r] in residual_labels)
            avail = [lab for lab in residual_labels if lab not in used]
            if not avail:
                best['h'] = max(best['h'], len(path))
                if len(path) >= s: best['path'] = list(path)
                return
            for lab in avail:
                a2 = dict(assign); a2[row] = lab
                complete(a2, path + [(row, lab)], pos + 1)
                if best['path'] is not None: return
        complete(assign, path, 0)
    rec(dict(assign), [])
    return best['h'], best['path']

def consistent_free_labels(term, row, free_labels):
    lits = term[row]
    return sorted(l for l in free_labels if all(bit(l, t) == v for t, v in lits))

def encode(F, mu, R, pi, n, N, s):
    assign = dict(mu)                       # outside assignment
    free_out = sorted(set(range(N, n)) - set(mu.values()))
    rest = list(pi); code_assign = dict(mu); moved = []; deltas = []; rounds = 0; betas = []
    while rest:
        idx, st, rows = first_surviving(F, assign)
        assert idx is not None and st == 'free'
        term = F[idx]
        unc = [r for r in rows if r not in assign]
        k = min(len(unc), len(rest))
        pi_i = rest[:k]
        assert [r for r, _ in pi_i] == unc[:k], "path rows differ from the term's uncovered rows in order"
        moved_rows = set(r for r, _ in pi_i); betas.append(tuple(1 if r in moved_rows else 0 for r in term))
        for (r, lab) in pi_i:
            cons = consistent_free_labels(term, r, free_out)
            assert cons, "not rich: no consistent free outside label"
            ol = cons[0]                     # any consistent free label works; take the smallest
            free_out.remove(ol)
            code_assign[r] = ol; moved.append(r); deltas.append(lab)
        for (r, lab) in pi_i: assign[r] = lab
        rest = rest[k:]; rounds += 1
    return (tuple(sorted(code_assign.items())), tuple(betas), tuple(deltas)), rounds

def decode(F, code, n, N, s):
    code_assign, betas, deltas = code
    cur = dict(code_assign); d = 0; pis = []
    for beta in betas:
        idx, st, rows = first_surviving(F, cur)
        assert idx is not None and st != 'false'
        term = F[idx]
        sigma_rows = [r for r, flag in zip(term, beta) if flag]
        pi_i = []
        for r in sigma_rows:
            pi_i.append((r, deltas[d])); d += 1
        for r, lab in pi_i:
            cur[r] = lab
        pis.append(pi_i)
    for pi_i in pis:
        for r, _ in pi_i: cur.pop(r, None)
    return tuple(sorted(cur.items()))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--L', type=int, default=3); ap.add_argument('--L2', type=int, default=1)
    ap.add_argument('--e', type=int, default=2); ap.add_argument('--r', type=int, default=2)
    ap.add_argument('--s', type=int, default=2); ap.add_argument('--terms', type=int, default=6)
    ap.add_argument('--seed', type=int, default=20260918); ap.add_argument('--out', required=True)
    ap.add_argument('--max-restrictions', type=int, default=5_000_000,
                    help='refuse to enumerate a family larger than this (default 5e6)')
    a = ap.parse_args()
    n = 2 ** a.L; N = 2 ** a.L2; e = a.e; s = a.s
    rng = random.Random(a.seed)
    F = []
    while len(F) < a.terms:
        rows = rng.sample(range(n + 1), rng.randint(1, a.r))
        term = {}
        budget = a.r
        for row in rows:
            k = rng.randint(1, max(1, budget - (len(rows) - len(term) - 1)))
            k = min(k, a.L)
            bits = rng.sample(range(a.L), k); term[row] = [(t, rng.randint(0, 1)) for t in bits]
            budget -= k
        F.append(term)
    residual_labels = list(range(N)); O = list(range(N, n)); q = n + 1 - (N + 1 + e)
    if q < 0: sys.exit('e too large: no pigeons left to match')
    size = math.comb(n + 1, q) * math.factorial(n - N) // math.factorial(e)
    print(f'family size |Phi_e| = {size}', file=sys.stderr)
    if size > a.max_restrictions:
        sys.exit(f'refusing to enumerate {size} restrictions (limit {a.max_restrictions}); shrink the case')
    total = bad = rich_bad = failures = 0
    for matched in itertools.combinations(range(n + 1), q):
        for labs in itertools.permutations(O, q):
            mu = dict(zip(matched, labs)); total += 1
            holes = residual_labels + sorted(set(O) - set(labs))
            h, path = canonical_path(F, mu, holes, s)
            if h < s: continue
            bad += 1
            try:
                code, rounds = encode(F, mu, set(range(n + 1)) - set(matched), path[:s], n, N, s)
            except AssertionError as ex:
                if 'not rich' in str(ex): continue
                raise
            rich_bad += 1
            if decode(F, code, n, N, s) != tuple(sorted(mu.items())): failures += 1
    res = {'L': a.L, 'L2': a.L2, 'n': n, 'N': N, 'e': e, 'r': a.r, 's': s, 'seed': a.seed,
           'terms': [{str(k): v for k, v in t.items()} for t in F], 'restrictions': total, 'bad': bad,
           'rich_bad': rich_bad, 'round_trip_failures': failures}
    with open(a.out, 'a') as f: f.write(json.dumps(res) + '\n')
    print(json.dumps({k: v for k, v in res.items() if k != 'terms'}))
    return 0 if failures == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
