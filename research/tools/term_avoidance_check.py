#!/usr/bin/env python3
"""Cycle 220: how many random dense term-avoidance axioms does a low-degree PHP design tolerate?

Board: m rows, N holes, cell variables X[j][x] over F_2; system B = functional PHP axioms (Booleanity, row and hole
exclusions, row axioms sum_x X[j][x] = 1), system A = labelings (no hole exclusions).  m = N+1 is the PHP, m = N the
satisfiable bijective control.  A dense form is L = sum_j [x_j in H_j] + c with H_j a uniform subset of the holes
(--family uniform) or the zero set of a uniform affine function on F_2^l, N = 2^l (--family affine).  A term of
rank w is the flat L_1 = ... = L_w = 0 with indicator Z = prod_i (1 + L_i); the avoidance axiom is Z = 0 (for w = 1
the parity constraint L = 1).  Axioms are added one at a time to the degree-d polynomial-calculus closure of the
board (closure as in php_relative_image_check.py: echelon basis with degree-monotone pivots, elements of degree
<= d-1 multiplied by every variable until nothing grows), and the tool reports the first count a* at which 1 enters
the closure, with the closure dimension after every axiom.
Usage: term_avoidance_check.py --N 8 --d 3 --w 1 --family affine --seeds 1,2,3 --max-a 80 --out FILE"""
import argparse, itertools, json, random, time

class Board:
    def __init__(self, N, m, system, dmax):
        self.N = N; self.m = m; self.B = (system == 'B'); self.dmax = dmax
        self.monos = []; self.index = {}
        for k in range(dmax + 1):
            for rows in itertools.combinations(range(m), k):
                for holes in (itertools.permutations(range(N), k) if self.B else itertools.product(range(N), repeat=k)):
                    t = tuple(zip(rows, holes)); self.index[t] = len(self.monos); self.monos.append(t)
        self.deg = [len(t) for t in self.monos]
        self.table = {}

    def var_table(self, j, x):
        key = (j, x)
        if key not in self.table:
            tab = []
            for t in self.monos:
                u = self.mul_mono(t, j, x)
                tab.append(-1 if u is None or len(u) > self.dmax else self.index[u])
            self.table[key] = tab
        return self.table[key]

    def mul_mono(self, t, j, x):
        for (jj, xx) in t:
            if jj == j: return t if xx == x else None
            if self.B and xx == x: return None
        return tuple(sorted(t + ((j, x),)))

    def mul_var(self, vec, j, x):
        tab = self.var_table(j, x); out = 0
        while vec:
            h = vec.bit_length() - 1; vec ^= 1 << h
            u = tab[h]
            if u >= 0: out ^= 1 << u
        return out

    def mul_form(self, vec, H, c):
        out = vec if c else 0
        for j, Hj in enumerate(H):
            for x in Hj: out ^= self.mul_var(vec, j, x)
        return out

class Closure:
    def __init__(self, board, d):
        self.b = board; self.d = d; self.basis = {}; self.done = set()
        for i, t in enumerate(board.monos):
            if len(t) > d - 1: break
            dom = {j for j, _ in t}
            for j in range(board.m):
                if j in dom: continue
                v = 1 << i
                for x in range(board.N):
                    u = board.mul_mono(t, j, x)
                    if u is not None: v ^= 1 << board.index[u]
                self.insert(v)
        self.close()

    def insert(self, v):
        basis = self.basis
        while v:
            h = v.bit_length() - 1
            if h in basis: v ^= basis[h]
            else: basis[h] = v; return True
        return False

    def close(self):
        b = self.b
        while True:
            low = [v for h, v in self.basis.items() if b.deg[h] <= self.d - 1 and v not in self.done]
            if not low or 0 in self.basis: break
            for v in low:
                self.done.add(v)
                for j in range(b.m):
                    for x in range(b.N):
                        self.insert(b.mul_var(v, j, x))

    def has_one(self): return 0 in self.basis

def dense_form(rng, N, m, family):
    if family == 'uniform':
        return [[x for x in range(N) if rng.random() < 0.5] for _ in range(m)], rng.randrange(2)
    l = N.bit_length() - 1; assert 1 << l == N
    H = []
    for _ in range(m):
        a = rng.randrange(N); c = rng.randrange(2)
        H.append([x for x in range(N) if (bin(a & x).count('1') + c) % 2 == 1])
    return H, rng.randrange(2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--N', type=int, required=True); ap.add_argument('--d', type=int, required=True)
    ap.add_argument('--w', type=int, default=1); ap.add_argument('--family', default='affine')
    ap.add_argument('--boards', default='php,bij,lab'); ap.add_argument('--seeds', default='1')
    ap.add_argument('--max-a', type=int, default=80); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = open(a.out, 'w')
    for name in a.boards.split(','):
        N = a.N; m, system = {'php': (N + 1, 'B'), 'bij': (N, 'B'), 'lab': (N + 1, 'A')}[name]
        t0 = time.time(); board = Board(N, m, system, a.d); base = Closure(board, a.d)
        base_dim = len(base.basis); base_state = (dict(base.basis), set(base.done))
        print(f'{name}: N={N} m={m} system={system} d={a.d} monomials={len(board.monos)} base closure={base_dim} '
              f'one_in_base={base.has_one()} ({time.time() - t0:.1f}s)', flush=True)
        for seed in [int(s) for s in a.seeds.split(',')]:
            rng = random.Random(1000 * seed + a.w)
            cl = base; cl.basis = dict(base_state[0]); cl.done = set(base_state[1])
            dims = []; tip = None; t1 = time.time()
            for count in range(1, a.max_a + 1):
                z = 1
                for _ in range(a.w):
                    H, c = dense_form(rng, N, m, a.family); z = board.mul_form(z, H, c ^ 1)
                cl.insert(z); cl.close(); dims.append(len(cl.basis))
                if cl.has_one(): tip = count; break
            rec = dict(board=name, N=N, m=m, system=system, d=a.d, w=a.w, family=a.family, seed=seed,
                       monomials=len(board.monos), base_closure=base_dim, tipping_count=tip, max_a=a.max_a,
                       closure_dims=dims, seconds=round(time.time() - t1, 1))
            out.write(json.dumps(rec) + '\n'); out.flush()
            print(f'  seed {seed}: w={a.w} {a.family}: tipping count {tip} (dims {dims[:3]}...{dims[-1]}, '
                  f'{rec["seconds"]}s)', flush=True)

if __name__ == '__main__':
    main()
