"""Feasibility count for a single-block conservativity test over a hard old base (route review).
Base: Tseitin constraints over F3 on a small cubic graph, variables = edges (Boolean), vertex
constraint prod_{e at v}(1 - 2 x_e) = (-1)^{charge_v}.  For D = 6, 7, 8 report the closure dimension,
the semantic dimension (degree-<=D polynomials vanishing on the solution set; all of R_{<=D} if the
charges are inconsistent), and whether 1 is in the closure.  A test of one fresh block is nonvacuous
only where the closure is below the semantic dimension."""
import itertools, json, os, sys
import numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_c3_conservativity_20260922'))
from conservativity import Space, closure, const, padd, pmul, var, contains_one
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3

GRAPHS = {
    'K33': [(0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)],
    'Q3': [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)],
    'Petersen': [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 5), (1, 6), (2, 7), (3, 8), (4, 9),
                 (5, 7), (7, 9), (9, 6), (6, 8), (8, 5)],
}

def tseitin(edges, charges):
    m = len(edges); verts = sorted({u for e in edges for u in e}); gens = []
    for v in verts:
        p = const(1, m)
        for k, e in enumerate(edges):
            if v in e: p = pmul(p, padd(const(1, m), var(k, m), -2), m)
        gens.append(padd(p, const(-1 if charges[v] else 1, m), -1))
    return gens

def work(job):
    name, D, odd = job
    edges = GRAPHS[name]; m = len(edges); verts = sorted({u for e in edges for u in e})
    charges = {v: (1 if (odd and v == 0) else 0) for v in verts}
    gens = tseitin(edges, charges)
    sp = Space(m, 0, D); P, W, piv = closure(sp, gens)
    if odd:
        semantic = sp.cols
    else:
        pts = np.array(list(itertools.product(range(2), repeat=m)), dtype=np.int64)
        sol = [pt for pt in pts if all(sum(c * int(np.prod([x ** a for x, a in zip(pt, e)])) for e, c in g.items()) % 3 == 0 for g in gens)]
        E = np.array(sp.mons, dtype=np.int64)
        V = np.array([[int(np.prod([x ** a for x, a in zip(pt, e)])) % 3 for e in E] for pt in sol], dtype=np.uint8)
        semantic = sp.cols - gf3.rank(V)
    return dict(graph=name, m=m, D=D, charges='odd' if odd else 'even', cols=sp.cols, dim=int(P.shape[0]),
                semantic=int(semantic), one=bool(contains_one(sp, P, W)))

if __name__ == '__main__':
    jobs = [(g, D, odd) for g in GRAPHS for D in (6, 7, 8) for odd in (False, True)]
    with Pool(12) as pool: res = pool.map(work, jobs)
    for r in res: print(json.dumps(r))
    json.dump(res, open(os.path.join(HERE, 'proxy_count.json'), 'w'), indent=1)
