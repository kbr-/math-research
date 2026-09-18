#!/usr/bin/env python3
"""Cycle 218: does adjoining ENS blocks on dense forms lower the PC refutation degree of the small functional PHP?

Base: functional PHP over F_2 on N+1 rows and N holes (Booleanity, row and hole exclusions built into the monomials,
row axioms Q_j as generators).  A block with inputs L_1..L_rho (dense forms L = sum_j [x_j in H_j] + c) and accuracy
h = 1 has fresh Boolean coefficient variables r_1..r_rho, product P = 1 - sum_j r_j L_j and companions L_i P.
Monomials are (partial matching, set of r variables) of total degree <= d, ordered by total degree.  The tool computes
the degree-d polynomial-calculus closure of the row axioms and all companions and reports whether it contains 1.
A design extension (a functional with value 1 at 1 vanishing on the closure) exists exactly when it does not.
It also reports dim(closure ∩ old polynomials); equality with the base closure (run with --blocks '') means the block
adds no consequence among the old variables through degree d.
Provably conservative controls: rho = 1 (substitute r = 1) and rho = 2 (substitute r_1 = 1, r_2 = 1 + L_1, of degree
one).  For rho = 3 the natural substitution has degree two and certifies conservativity only one degree higher.
Usage: augmented_php_degree.py --N 8 --d 4 --blocks 3 [--blocks 3,3] [--affine] [--seed 1] --out FILE"""
import argparse, itertools, json, random, resource, time

class Ext:
    def __init__(self, N, R, d):
        self.N = N; self.m = N + 1; self.R = R; self.d = d; self.monos = []; self.index = {}
        xs = {k: [tuple(zip(rows, holes)) for rows in itertools.combinations(range(self.m), k)
                  for holes in itertools.permutations(range(N), k)] for k in range(d + 1)}
        for total in range(d + 1):
            for l in range(min(R, total) + 1):
                for rs in itertools.combinations(range(R), l):
                    for t in xs[total - l]:
                        self.index[(t, rs)] = len(self.monos); self.monos.append((t, rs))
        self.deg = [len(t) + len(rs) for t, rs in self.monos]

    def mul_x(self, mono, j, x):
        t, rs = mono
        for (jj, xx) in t:
            if jj == j: return mono if xx == x else None
            if xx == x: return None
        return (tuple(sorted(t + ((j, x),))), rs)

    def mul_r(self, mono, i):
        t, rs = mono
        return mono if i in rs else (t, tuple(sorted(rs + (i,))))

    def apply(self, vec, fn):
        out = 0
        while vec:
            h = vec.bit_length() - 1; vec ^= 1 << h
            u = fn(self.monos[h])
            if u is not None: out ^= 1 << self.index[u]
        return out

    def mul_form(self, vec, H, c):
        out = vec if c else 0
        for j, Hj in enumerate(H):
            for x in Hj: out ^= self.apply(vec, lambda mo: self.mul_x(mo, j, x))
        return out

    def mul_mono_vec(self, vec, mono):
        t, rs = mono
        for (j, x) in t: vec = self.apply(vec, lambda mo: self.mul_x(mo, j, x))
        for i in rs: vec = self.apply(vec, lambda mo: self.mul_r(mo, i))
        return vec

def closure(E, companions):
    d = E.d; basis = {}
    def insert(v):
        while v:
            h = v.bit_length() - 1
            if h in basis: v ^= basis[h]
            else: basis[h] = v; return True
        return False
    for i, (t, rs) in enumerate(E.monos):
        if E.deg[i] > d - 1: break
        dom = {j for j, _ in t}
        for j in range(E.m):
            if j in dom: continue
            v = 1 << i
            for x in range(E.N):
                u = E.mul_x((t, rs), j, x)
                if u is not None: v ^= 1 << E.index[u]
            insert(v)
    base_dim = len(basis)
    for comp, cdeg in companions:
        for i, mono in enumerate(E.monos):
            if E.deg[i] + cdeg > d: break
            insert(E.mul_mono_vec(comp, mono))
    ns_dim = len(basis); done = set(); rounds = 0
    variables = [('x', j, x) for j in range(E.m) for x in range(E.N)] + [('r', i) for i in range(E.R)]
    while True:
        low = [v for h, v in basis.items() if E.deg[h] <= d - 1 and v not in done]
        if not low: break
        rounds += 1; grew = False
        for v in low:
            done.add(v)
            for var in variables:
                if var[0] == 'x': w = E.apply(v, lambda mo: E.mul_x(mo, var[1], var[2]))
                else: w = E.apply(v, lambda mo: E.mul_r(mo, var[1]))
                grew |= insert(w)
        if not grew: break
    v = 1; one_in = False
    while v:
        h = v.bit_length() - 1
        if h not in basis: break
        v ^= basis[h]
    one_in = (v == 0)
    out = {'dim_T': len(E.monos), 'dim_base_NS': base_dim, 'dim_NS_with_companions': ns_dim, 'dim_closure': len(basis),
           'dim_closure_below_d': sum(1 for h in basis if E.deg[h] <= d - 1),
           'closure_rounds': rounds, 'one_in_closure': one_in}
    # old-only consequences: eliminate the monomials that carry new variables first; rows left without such
    # monomials span closure ∩ (old polynomials), because rows with a new-variable pivot have distinct leading
    # new-variable monomials and zeros above them among the new-variable monomials
    rmask = 0
    for i, (t, rs) in enumerate(E.monos):
        if rs: rmask |= 1 << i
    done.clear(); items = list(basis.values()); basis.clear(); second = {}; old_rows = 0
    while items:
        v = items.pop()
        while v:
            vr = v & rmask
            h = (vr.bit_length() - 1) if vr else (v.bit_length() - 1)
            if h in second: v ^= second[h]
            else:
                second[h] = v; old_rows += (0 if vr else 1); break
    out['dim_closure_old_only'] = old_rows
    return out

def half_sets(rng, N, m, affine):
    if not affine: return [sorted(rng.sample(range(N), N // 2)) for _ in range(m)]
    return [[x for x in range(N) if bin(aj & x).count('1') & 1] for aj in (rng.randrange(N) for _ in range(m))]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--N', type=int, required=True); ap.add_argument('--d', type=int, required=True)
    ap.add_argument('--blocks', default='', help='comma list of input counts, one entry per block; empty for the base system')
    ap.add_argument('--fake-control', action='store_true', help='replace the companions of a one-input block by non-conservative axioms')
    ap.add_argument('--affine', action='store_true'); ap.add_argument('--seed', type=int, default=1); ap.add_argument('--out', required=True)
    a = ap.parse_args(); rng = random.Random(a.seed); N = a.N; m = N + 1
    sizes = [int(b) for b in a.blocks.split(',') if b]; R = sum(sizes); t0 = time.time()
    E = Ext(N, R, a.d); companions = []; offset = 0
    for rho in sizes:
        forms = [(half_sets(rng, N, m, a.affine), rng.getrandbits(1)) for _ in range(rho)]
        P = 1
        for k, (H, c) in enumerate(forms):
            P ^= E.apply(E.mul_form(1, H, c), lambda mo: E.mul_r(mo, offset + k))
        for H, c in forms: companions.append((E.mul_form(P, H, c), 3))
        offset += rho
    if a.fake_control:
        # positive control for the old-only count: the non-conservative axioms r_0 = 1 and r_0 (1 + X_00) = 0 force X_00 = 1
        r0 = 1 << E.index[((), (0,))]; x00r0 = 1 << E.index[(((0, 0),), (0,))]
        companions = [(r0 ^ 1, 1), (x00r0 ^ r0, 2)]
    rec = {'N': N, 'd': a.d, 'blocks': sizes, 'affine': a.affine, 'seed': a.seed, 'fake_control': a.fake_control}
    rec.update(closure(E, companions))
    rec['seconds'] = round(time.time() - t0, 1); rec['max_rss_mb'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
    print(json.dumps(rec), flush=True)
    with open(a.out, 'a') as f: f.write(json.dumps(rec) + '\n')

if __name__ == '__main__':
    main()
