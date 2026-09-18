#!/usr/bin/env python3
"""Exact round-trip test of the encoding for mixed-term readers with hole queries.

Labels are 0..n-1 with n = 2^L; Q is a uniformly random affine subspace of dimension L2 (N = 2^L2 points).
Family Phi_e: choose the residual pigeon set R of size N+1+e among the n+1 pigeons and an injection mu of
the other pigeons into the outside labels O = [n] \\ Q (e outside labels stay free, the set E).
A reader F is an ordered list of terms; a term has an optional pinned pair (i, x) with i in the pinned-row
set A and a light tail {row -> literals} on rows of the light-row set B (A and B disjoint unless --two-role).
The canonical mixed tree: at a node, take the earliest non-falsified term whose pinned pair is matched by
mu if one exists, else the earliest non-falsified term; query all its uncovered tail rows in order (pigeon
queries over the available holes Q u E); then, if the term is still alive with its pinned pair unkilled,
make a heavy query: the pigeon i if i has at least two unkilled pinned pairs, else the hole x (branches: an
unassigned residual row moved to x, or the empty branch).  With --hole-only the heavy query is always the
hole x (the corrected rule: trigger holes are then distinct along a path).  Heights count queries.  For every restriction
with a path of at least h queries whose free labels are rich enough, the lexicographically first such
path is encoded (code restriction with the light rows moved to consistent free outside labels avoiding the
pinned labels, per-round star vectors, recorded answers) and decoded back.  Pinned rows are never moved.
--two-role draws tails from all rows, so a row may be pinned in one term and light in another; the decoder
is then expected to fail on some paths (negative control for the two-role correction).
"""
import argparse, itertools, json, math, random, sys

def bit(label, t): return (label >> t) & 1

def consistent(lits, label): return all(bit(label, t) == v for t, v in lits)

def status(term, assign, emptied):
    """('false',None,None) | ('true',None,None) | ('free', uncovered_tail_rows, pin_alive)."""
    free = []
    for row, lits in term['tail']:
        if row in assign:
            if not consistent(lits, assign[row]): return 'false', None, None
        else:
            free.append(row)
    pin = term['pin']; pin_alive = False
    if pin is not None:
        i, x = pin
        if i in assign:
            if assign[i] != x: return 'false', None, None
        else:
            if x in emptied or x in set(assign.values()): return 'false', None, None
            pin_alive = True
    if not free and not pin_alive: return 'true', None, None
    return 'free', free, pin_alive

def pick_term(F, assign, emptied, base):
    """Matched-first preference; base gives the restriction's matching for pinned rows."""
    first = None
    for idx, term in enumerate(F):
        st, rows, pa = status(term, assign, emptied)
        if st == 'false': continue
        pin = term['pin']
        if pin is not None and base.get(pin[0]) == pin[1]:
            return idx, st, rows, pa
        if first is None: first = (idx, st, rows, pa)
    return first if first is not None else (None, None, None, None)

HOLE_ONLY = False

def unkilled_pairs(F, i, assign, emptied, holes_all):
    if HOLE_ONLY: return 1
    used = set(assign.values())
    return len(set(t['pin'][1] for t in F if t['pin'] is not None and t['pin'][0] == i
                   and t['pin'][1] in holes_all and t['pin'][1] not in used and t['pin'][1] not in emptied))

def first_long_path(F, mu, R, holes_all, h):
    """Lexicographically first path with at least h queries; also the height and the max heavy count."""
    best = {'path': None, 'height': 0, 'heavy': 0}
    def leaf(path, heavy):
        best['height'] = max(best['height'], len(path)); best['heavy'] = max(best['heavy'], heavy)
        if len(path) >= h and best['path'] is None: best['path'] = list(path)
    def rec(assign, emptied, path, heavy):
        if best['path'] is not None: return
        if len(path) >= h: leaf(path, heavy); return
        idx, st, rows, pa = pick_term(F, assign, emptied, mu)
        if idx is None or st == 'true': leaf(path, heavy); return
        term = F[idx]
        def tail(assign, path, pos):
            if best['path'] is not None: return
            if len(path) >= h: leaf(path, heavy); return
            while pos < len(rows) and rows[pos] in assign: pos += 1
            if pos == len(rows): after_tail(assign, path); return
            row = rows[pos]
            used = set(assign.values()); avail = sorted(l for l in holes_all if l not in used and l not in emptied)
            if not avail: leaf(path, heavy); return
            for lab in avail:
                a2 = dict(assign); a2[row] = lab
                tail(a2, path + [('L', row, lab)], pos + 1)
                if best['path'] is not None: return
        def after_tail(assign, path):
            st2, rows2, pa2 = status(term, assign, emptied)
            if st2 == 'false': rec(assign, emptied, path, heavy); return
            if st2 == 'true': leaf(path, heavy); return
            i, x = term['pin']
            if len(path) >= h: leaf(path, heavy); return
            if unkilled_pairs(F, i, assign, emptied, holes_all) >= 2:
                used = set(assign.values()); avail = sorted(l for l in holes_all if l not in used and l not in emptied)
                for lab in avail:
                    a2 = dict(assign); a2[i] = lab
                    rec(a2, emptied, path + [('P', i, lab)], heavy + 1)
                    if best['path'] is not None: return
            else:
                for j in sorted(r for r in R if r not in assign):
                    a2 = dict(assign); a2[j] = x
                    rec(a2, emptied, path + [('H', x, j)], heavy + 1)
                    if best['path'] is not None: return
                rec(assign, emptied | {x}, path + [('H', x, None)], heavy + 1)
        tail(dict(assign), path, 0)
    rec(dict(mu), frozenset(), [], 0)
    return best

class NotRich(Exception): pass

def encode(F, mu, R, path, free_out, holes_all, move_pinned_rows=False):
    assign = dict(mu); emptied = set(); code = dict(mu); free_out = sorted(free_out)
    betas = []; deltas = []; pos = 0
    while pos < len(path):
        idx, st, rows, pa = pick_term(F, assign, emptied, mu)
        assert idx is not None and st == 'free'
        term = F[idx]; flags = []
        for row, lits in term['tail']:
            if row in assign or pos >= len(path) or path[pos][0] != 'L':
                flags.append(0); continue
            kind, prow, lab = path[pos]
            assert prow == row, 'path row differs from the term row order'
            cons = [l for l in free_out if consistent(lits, l)]
            if not cons: raise NotRich()
            code[row] = cons[0]; free_out.remove(cons[0])
            assign[row] = lab; deltas.append(lab); flags.append(1); pos += 1
        heavy = 0
        st2, rows2, pa2 = status(term, assign, emptied)
        if st2 == 'free' and pa2 and pos < len(path):
            assert path[pos][0] in ('P', 'H'), 'an alive pinned pair must be followed by a heavy query'
            kind, key, ans = path[pos]; i, x = term['pin']
            if kind == 'P':
                assert key == i and unkilled_pairs(F, i, assign, emptied, holes_all) >= 2
                assign[i] = ans; deltas.append(('lab', ans))
            else:
                assert key == x and unkilled_pairs(F, i, assign, emptied, holes_all) < 2
                if ans is None: emptied.add(x); deltas.append(('empty', None))
                else: assign[ans] = x; deltas.append(('row', ans))
            heavy = 1; pos += 1
        betas.append((tuple(flags), heavy))
    return (tuple(sorted(code.items())), tuple(betas), tuple(deltas))

def decode(F, code, holes_all):
    code_assign, betas, deltas = code
    cur = dict(code_assign); emptied = set(); d = 0; touched = []
    for flags, heavy in betas:
        idx, st, rows, pa = pick_term(F, cur, emptied, dict(code_assign))
        if idx is None or st == 'false': return None
        term = F[idx]
        for (row, lits), flag in zip(term['tail'], flags):
            if flag:
                cur[row] = deltas[d]; d += 1; touched.append(row)
        if heavy:
            st2, rows2, pa2 = status(term, cur, emptied)
            if st2 != 'free' or not pa2: return None
            i, x = term['pin']
            if unkilled_pairs(F, i, cur, emptied, holes_all) >= 2:
                kind, val = deltas[d]; d += 1
                if kind != 'lab': return None
                cur[i] = val; touched.append(i)
            else:
                kind, val = deltas[d]; d += 1
                if kind == 'empty': emptied.add(x)
                elif kind == 'row': cur[val] = x; touched.append(val)
                else: return None
    for row in touched: cur.pop(row, None)
    return tuple(sorted(cur.items()))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--L', type=int, default=3); ap.add_argument('--L2', type=int, default=1)
    ap.add_argument('--e', type=int, default=1); ap.add_argument('--w', type=int, default=1)
    ap.add_argument('--h', type=int, default=3); ap.add_argument('--terms', type=int, default=6)
    ap.add_argument('--pinned-rows', type=int, default=5, help='size of the pinned-row set A')
    ap.add_argument('--tail-rows', type=int, default=2, help='maximum tail rows per term')
    ap.add_argument('--seed', type=int, default=20260918); ap.add_argument('--out', required=True)
    ap.add_argument('--two-role', action='store_true', help='tails may use pinned rows (negative control)')
    ap.add_argument('--two-role-example', action='store_true',
                    help='fixed reader: row 0 pinned in the first term and light in the second (expected to fail)')
    ap.add_argument('--max-restrictions', type=int, default=2_000_000)
    ap.add_argument('--hole-only', action='store_true', help='always query the trigger hole (corrected rule)')
    a = ap.parse_args()
    global HOLE_ONLY; HOLE_ONLY = a.hole_only
    n = 2 ** a.L; N = 2 ** a.L2; e = a.e; rng = random.Random(a.seed)
    while True:
        vecs = [rng.randrange(n) for _ in range(a.L2)]; span = {0}
        for v in vecs: span |= {x ^ v for x in span}
        if len(span) == N: break
    tr = rng.randrange(n); Q = set(x ^ tr for x in span); O = sorted(set(range(n)) - Q)
    rows_all = list(range(n + 1)); A = sorted(rng.sample(rows_all, a.pinned_rows))
    B = rows_all if a.two_role else [r for r in rows_all if r not in A]
    F = []
    while len(F) < a.terms:
        kind = rng.random()
        pin = None
        if kind < 0.85: pin = (rng.choice(A), rng.randrange(n))
        tail = []
        if kind > 0.1:
            for row in rng.sample(B, rng.randint(1, a.tail_rows)):
                if pin is not None and row == pin[0]: continue
                bits = rng.sample(range(a.L), rng.randint(1, a.w)); tail.append((row, [(t, rng.randint(0, 1)) for t in bits]))
        if pin is None and not tail: continue
        F.append({'pin': pin, 'tail': tail})
    if a.two_role_example:
        q0, q1 = sorted(Q)[:2]; A = [0, 1, 2, 3]
        F = [{'pin': (0, q0), 'tail': [(5, [(0, 0)])]}, {'pin': (1, q1), 'tail': [(0, [(1, 0)])]},
             {'pin': None, 'tail': [(6, [(2, 1)])]}]
        a.two_role = True
    pinned_labels = set(t['pin'][1] for t in F if t['pin'] is not None)
    q = n + 1 - (N + 1 + e)
    size = math.comb(n + 1, q) * math.factorial(n - N) // math.factorial(e)
    print(f'family size |Phi_e| = {size}', file=sys.stderr)
    if size > a.max_restrictions: sys.exit(f'refusing to enumerate {size} restrictions (limit {a.max_restrictions})')
    total = bad = rich = failures = 0; max_heavy = 0; heavy_hist = {}
    for matched in itertools.combinations(rows_all, q):
        R = set(rows_all) - set(matched)
        for labs in itertools.permutations(O, q):
            mu = dict(zip(matched, labs)); total += 1
            E = sorted(set(O) - set(labs)); holes_all = sorted(Q) + E
            res = first_long_path(F, mu, R, holes_all, a.h)
            max_heavy = max(max_heavy, res['heavy']); heavy_hist[res['heavy']] = heavy_hist.get(res['heavy'], 0) + 1
            if res['path'] is None: continue
            bad += 1
            try:
                code = encode(F, mu, R, res['path'][:a.h], [l for l in E if l not in pinned_labels], holes_all)
            except NotRich:
                continue
            rich += 1
            if decode(F, code, holes_all) != tuple(sorted(mu.items())): failures += 1
    rec = {'L': a.L, 'L2': a.L2, 'n': n, 'N': N, 'e': e, 'w': a.w, 'h': a.h, 'seed': a.seed, 'two_role': a.two_role,
           'hole_only': a.hole_only,
           'Q': sorted(Q), 'A': A, 'terms': [{'pin': t['pin'], 'tail': [[r, l] for r, l in t['tail']]} for t in F],
           'restrictions': total, 'bad': bad, 'rich_bad': rich, 'round_trip_failures': failures,
           'max_heavy_queries': max_heavy, 'heavy_histogram': {str(k): v for k, v in sorted(heavy_hist.items())}}
    with open(a.out, 'a') as f: f.write(json.dumps(rec) + '\n')
    print(json.dumps({k: v for k, v in rec.items() if k not in ('terms', 'Q', 'A')}))
    return 0 if failures == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
