#!/usr/bin/env python3
"""Cycle 217: do the hole axioms lower the image degree of a flat indicator on dense forms?

Board: m = N+1 rows, N holes, cell variables X[j][x] over F_2.  System A: Booleanity, row exclusions, row axioms
Q_j = sum_x X[j][x] - 1 (labelings).  System B adds the hole exclusions X[j][x] X[j'][x] (functional PHP).
Monomials are partial labelings (A) or partial matchings (B) of at most d rows.  V_d is the degree-d polynomial
calculus closure of the row axioms inside the span T_d of these monomials: start from t*Q_j (|t| <= d-1) and close
under multiplying elements of degree <= d-1 by variables (elements of degree <= d-1 are read off an echelon basis
whose pivots prefer high degree).

Image test for a reader of rank-one terms [L_i = 1], i <= rho, on dense forms L_i = sum_j [x_j in H_ij] + c_i:
the block product is P = prod_i (1 + L_i), the indicator of the flat L_1 = ... = L_rho = 0.  For a parameter s the
linear image conditions are: P-hat in T_s, U_i in T_{s-1}, 1 + P-hat + sum_i U_i L_i in V_s, L_i P-hat in V_{s+1}.
(The Booleanity condition is not imposed: infeasibility is then definitive, feasibility is a necessary condition.)
Mode --rank2 (system B, degree-4 closure): readers of rank-two terms t_k = (1 + L_k)(1 + L'_k) at s = w = 2, with
unknown P-hat in T_2 and constants U_k; without the hole axioms an image must equal P on labelings, so a nonzero
three-row mixed difference of P (checked at function level) excludes it.
Usage: php_relative_image_check.py --N 6 --out FILE [--seed 1] [--rank2]"""
import argparse, itertools, json, random, time

class Board:
    def __init__(self, N, system, dmax):
        self.N = N; self.m = N + 1; self.B = (system == 'B'); self.dmax = dmax
        self.monos = []; self.index = {}
        for k in range(dmax + 1):
            for rows in itertools.combinations(range(self.m), k):
                for holes in (itertools.permutations(range(N), k) if self.B else itertools.product(range(N), repeat=k)):
                    t = tuple(zip(rows, holes)); self.index[t] = len(self.monos); self.monos.append(t)
        self.deg = [len(t) for t in self.monos]
        self.first = {k: next(i for i, t in enumerate(self.monos) if len(t) == k) for k in range(dmax + 1)}

    def mul_mono(self, t, j, x):
        for (jj, xx) in t:
            if jj == j: return t if xx == x else None
            if self.B and xx == x: return None
        return tuple(sorted(t + ((j, x),)))

    def mul_var(self, vec, j, x):
        out = 0
        while vec:
            h = vec.bit_length() - 1; vec ^= 1 << h
            t = self.mul_mono(self.monos[h], j, x)
            if t is not None: out ^= 1 << self.index[t]
        return out

    def mul_form(self, vec, H, c):
        out = vec if c else 0
        for j, Hj in enumerate(H):
            for x in Hj: out ^= self.mul_var(vec, j, x)
        return out

    def closure(self, d):
        """Echelon basis (pivot -> vector) of V_d inside T_d; pivots prefer high index = high degree."""
        limit = self.first[d + 1] if d + 1 in self.first else len(self.monos)
        basis = {}
        def insert(v):
            while v:
                h = v.bit_length() - 1
                if h in basis: v ^= basis[h]
                else: basis[h] = v; return True
            return False
        for i, t in enumerate(self.monos):
            if len(t) > d - 1: break
            dom = {j for j, _ in t}
            for j in range(self.m):
                if j in dom: continue
                v = 1 << i
                for x in range(self.N):
                    u = self.mul_mono(t, j, x)
                    if u is not None: v ^= 1 << self.index[u]
                insert(v)
        ns_dim = len(basis); done = set(); rounds = 0
        while True:
            low = [v for h, v in basis.items() if self.deg[h] <= d - 1 and v not in done]
            if not low: break
            rounds += 1; grew = False
            for v in low:
                done.add(v)
                for j in range(self.m):
                    for x in range(self.N):
                        grew |= insert(self.mul_var(v, j, x))
            if not grew: break
        assert all(h < limit for h in basis)
        return basis, ns_dim, rounds

def normal_form(v, basis):
    out = 0
    while v:
        h = v.bit_length() - 1
        if h in basis: v ^= basis[h]
        else: out |= 1 << h; v ^= 1 << h
    return out

def solvable(columns, rhs):
    """Is rhs in the F_2-span of the columns (vectors as ints)?"""
    basis = {}
    for v in columns:
        while v:
            h = v.bit_length() - 1
            if h in basis: v ^= basis[h]
            else: basis[h] = v; break
    while rhs:
        h = rhs.bit_length() - 1
        if h not in basis: return False
        rhs ^= basis[h]
    return True

def image_test(board, closures, forms, s):
    Vs = closures[s][0]; Vs1 = closures[s + 1][0]; width = len(board.monos)
    rho = len(forms); cols = []
    for i, t in enumerate(board.monos):            # unknown coefficient of monomial t in P-hat
        if len(t) > s: break
        v = normal_form(1 << i, Vs)
        for k, (H, c) in enumerate(forms):
            v |= normal_form(board.mul_form(1 << i, H, c), Vs1) << (width * (k + 1))
        cols.append(v)
    for k, (H, c) in enumerate(forms):             # unknown coefficient of monomial t in U_k
        for i, t in enumerate(board.monos):
            if len(t) > s - 1: break
            cols.append(normal_form(board.mul_form(1 << i, H, c), Vs))
    return solvable(cols, normal_form(1, Vs))

def half_sets(rng, N, m, affine):
    """Per row a label set: a uniform half of the labels, or with --affine the set <a_j, x> = 1 for uniform a_j."""
    if not affine: return [sorted(rng.sample(range(N), N // 2)) for _ in range(m)]
    bits = N.bit_length() - 1; assert 2 ** bits == N
    out = []
    for _ in range(m):
        aj = rng.randrange(N); out.append([x for x in range(N) if bin(aj & x).count('1') & 1])
    return out

def mul_vec(board, u, g):
    out = 0
    while g:
        h = g.bit_length() - 1; g ^= 1 << h; w = u
        for (j, x) in board.monos[h]: w = board.mul_var(w, j, x)
        out ^= w
    return out

def term_vec(board, forms):
    v = 1                                   # the empty monomial has index 0
    for H, c in forms: v ^= board.mul_form(v, H, c)
    return v

def image_test_terms(board, closures, terms, s, w):
    """Inputs are terms t_k (vectors of degree w): 1 + P-hat + sum U_k t_k in V_s, t_k P-hat in V_{s+w}."""
    Vs = closures[s][0]; Vsw = closures[s + w][0]; width = len(board.monos); cols = []
    for i, t in enumerate(board.monos):
        if len(t) > s: break
        v = normal_form(1 << i, Vs)
        for k, tk in enumerate(terms): v |= normal_form(mul_vec(board, 1 << i, tk), Vsw) << (width * (k + 1))
        cols.append(v)
    for k, tk in enumerate(terms):
        for i, t in enumerate(board.monos):
            if len(t) > s - w: break
            cols.append(normal_form(mul_vec(board, 1 << i, tk), Vs))
    return solvable(cols, normal_form(1, Vs))

def row_degree_at_least_3(N, m, term_forms, rng, tries=400):
    """Function-level check for system A: a nonzero mixed difference of P over three rows."""
    def P(lab):
        for forms in term_forms:
            if all((sum(1 for j, Hj in enumerate(H) if lab[j] in Hj) + c) % 2 == 0 for H, c in forms): return 0
        return 1
    for _ in range(tries):
        lab = [rng.randrange(N) for _ in range(m)]; rows = rng.sample(range(m), 3); alt = [rng.randrange(N) for _ in rows]
        total = 0
        for eps in itertools.product((0, 1), repeat=3):
            l2 = lab[:]
            for r, e, b in zip(rows, eps, alt):
                if e: l2[r] = b
            total ^= P(l2)
        if total: return True
    return False

def rank_two_run(a):
    rng = random.Random(a.seed); N = a.N; m = N + 1; recs = []
    dense = lambda: (half_sets(rng, N, m, a.affine), rng.getrandbits(1))
    pin = lambda j: ([[0] if jj == j else [] for jj in range(m)], 1)
    readers = [(f'dense-rank2-a{n}-{r}', [[dense(), dense()] for _ in range(n)]) for n in (2, 4, 8) for r in range(2)]
    readers.append(('collision-control', [[pin(0), dense()], [pin(1), dense()]]))
    t0 = time.time(); board = Board(N, 'B', 4); closures = {}
    for d in (2, 4):
        basis, ns_dim, rounds = board.closure(d); closures[d] = (basis, ns_dim, rounds)
        rec = {'kind': 'closure', 'N': N, 'system': 'B', 'd': d, 'dim_T': board.first.get(d + 1, len(board.monos)),
               'dim_V': len(basis), 'dim_NS_span': ns_dim, 'closure_rounds': rounds,
               'one_in_V': normal_form(1, basis) == 0, 'seconds': round(time.time() - t0, 1)}
        print(json.dumps(rec), flush=True); recs.append(rec)
    for name, term_forms in readers:
        terms = [term_vec(board, forms) for forms in term_forms]
        rec = {'kind': 'image-rank2', 'N': N, 'system': 'B', 'affine': a.affine, 'reader': name, 'terms': len(terms), 's': 2, 'w': 2,
               'feasible_with_hole_axioms': image_test_terms(board, closures, terms, 2, 2),
               'P_row_degree_at_least_3_on_labelings': row_degree_at_least_3(N, m, term_forms, rng),
               'seconds': round(time.time() - t0, 1)}
        print(json.dumps(rec), flush=True); recs.append(rec)
    with open(a.out, 'a') as f:
        for r in recs: f.write(json.dumps(r) + '\n')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--N', type=int, required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=1); ap.add_argument('--dmax', type=int, default=3)
    ap.add_argument('--readers', type=int, default=3); ap.add_argument('--only', default='')
    ap.add_argument('--affine', action='store_true', help='forms with affine half-spaces of F_2^log2(N) as row label sets')
    ap.add_argument('--rank2', action='store_true', help='rank-two terms at s = w = 2 with the degree-4 closure (system B)')
    a = ap.parse_args()
    if a.rank2: return rank_two_run(a)
    rng = random.Random(a.seed); N = a.N; m = N + 1; recs = []
    def dense_form():
        return (half_sets(rng, N, m, a.affine), rng.getrandbits(1))
    def symmetric_form(Hset):
        return ([sorted(Hset) for _ in range(m)], 0)
    readers = []
    for r in range(a.readers):
        for rho in (2, 3):
            readers.append((f'dense-{rho}-{r}', [dense_form() for _ in range(rho)]))
    halves = [set(rng.sample(range(N), N // 2)) for _ in range(3)]
    readers.append(('symmetric-3', [symmetric_form(h) for h in halves]))
    # positive control: 1 + L_1 = [x_0 = 0], 1 + L_2 = [x_1 = 0], L_3 dense; the flat is empty only under the hole axioms
    pin = lambda j: ([[0] if jj == j else [] for jj in range(m)], 1)
    readers.append(('collision-control', [pin(0), pin(1), dense_form()]))
    for system in ('A', 'B'):
        t0 = time.time(); board = Board(N, system, a.dmax); closures = {}
        for d in range(1, a.dmax + 1):
            basis, ns_dim, rounds = board.closure(d); closures[d] = (basis, ns_dim, rounds)
            one_in = normal_form(1, basis) == 0
            rec = {'kind': 'closure', 'N': N, 'system': system, 'd': d, 'dim_T': board.first.get(d + 1, len(board.monos)),
                   'dim_V': len(basis), 'dim_NS_span': ns_dim, 'closure_rounds': rounds, 'one_in_V': one_in,
                   'seconds': round(time.time() - t0, 1)}
            print(json.dumps(rec), flush=True); recs.append(rec)
        for name, forms in readers:
            if a.only and name != a.only: continue
            for s in range(1, a.dmax):
                ok = image_test(board, closures, forms, s)
                rec = {'kind': 'image', 'N': N, 'system': system, 'affine': a.affine, 'reader': name, 'rho': len(forms), 's': s, 'feasible': ok}
                print(json.dumps(rec), flush=True); recs.append(rec)
    with open(a.out, 'a') as f:
        for r in recs: f.write(json.dumps(r) + '\n')

if __name__ == '__main__':
    main()
