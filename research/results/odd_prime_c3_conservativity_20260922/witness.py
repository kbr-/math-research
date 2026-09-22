"""Extract and check the existing-variable elements that a fresh block adds (two-block base).

Usage: witness.py TAG D SEED...  Checks, independently of the fresh-first bookkeeping: (1) the
element lies in the full closure (by construction: it is a row of the full closure's echelon
basis); (2) it is not in the base closure, tested by rank in the existing ring's own coordinates;
(3) it vanishes at every solution of the base system (semantic soundness); (4) it lies in the
base closure at D+1 or D+2 (degree lag)."""
import itertools, json, sys
import numpy as np
from conservativity import *

def elements(inst):
    v, D = inst['v'], inst['D']; base_forms, fresh_forms = inst['base'], inst['fresh']
    tA = sum(len(b) for b in base_forms); tB = len(fresh_forms)
    sp0 = Space(v, tA, D); gens0, k = [], v
    for b in base_forms:
        gens0 += block_generators(b, list(range(k, k + len(b))), v, v + tA); k += len(b)
    P0, W0, _ = closure(sp0, gens0); B0 = dense(P0, W0, sp0)
    fv = list(range(v + tA, v + tA + tB)); sp1 = Space(v, tA + tB, D, fresh_vars=fv)
    gens1 = [{e + (0,) * tB: c for e, c in g.items()} for g in gens0]
    gens1 += block_generators(fresh_forms, fv, v, v + tA + tB)
    P1, W1, _ = closure(sp1, gens1); B1 = dense(P1, W1, sp1)
    E, piv = echelon(B1[:, sp1.fresh_first], False)
    ex = E[piv >= sp1.nfresh][:, sp1.nfresh:]           # existing part, fresh-first coordinates
    exmons = [sp1.mons[i] for i in sp1.fresh_first[sp1.nfresh:]]
    polys = [{m[:v + tA]: int(c) for m, c in zip(exmons, row) if c} for row in ex]
    new = []
    r0 = B0.shape[0]; cur = B0
    for p in polys:
        w = sp0.vec(p)
        if gf3.rank(np.vstack([cur, w])) > cur.shape[0]:
            new.append(p); cur = np.vstack([cur, w])
    return dict(sp0=sp0, gens0=gens0, B0=B0, B1=B1, sp1=sp1, new=new, v=v, tA=tA)

def evaluate(p, pt):
    s = 0
    for e, c in p.items():
        t = c
        for a, x in zip(e, pt): t *= x ** a
        s += t
    return s % 3

def solutions(gens, v, tA):
    for xs in itertools.product(range(2), repeat=v):
        for rs in itertools.product(range(3), repeat=tA):
            pt = xs + rs
            if all(evaluate(g, pt) == 0 for g in gens): yield pt

def fmt(p, v):
    names = [f'x{i}' for i in range(v)] + [f'a{i}' for i in range(len(next(iter(p))) - v)]
    terms = []
    for e, c in sorted(p.items(), key=lambda t: (-sum(t[0]), t[0])):
        m = '*'.join(n + (f'^{a}' if a > 1 else '') for n, a in zip(names, e) if a)
        terms.append(f'{c}' + ('*' + m if m else ''))
    return ' + '.join(terms)

if __name__ == '__main__':
    out = []
    tag, D0 = sys.argv[1], int(sys.argv[2])
    for seed in map(int, sys.argv[3:]):
        inst = make(tag, 6, D0, 2, 2, seed, 'random', 2)
        R = elements(inst)
        sols = list(solutions(R['gens0'], R['v'], R['tA']))
        rec = dict(name=inst['name'], base=inst['base'], fresh=inst['fresh'], n_base_solutions=len(sols),
                   new=[])
        for p in R['new']:
            d = max(sum(e) for e in p)
            sound = all(evaluate(p, pt) == 0 for pt in sols)
            lag = None
            for D2 in (D0 + 1, D0 + 2):
                sp2 = Space(R['v'], R['tA'], D2); P2, W2, _ = closure(sp2, R['gens0']); B2 = dense(P2, W2, sp2)
                if gf3.rank(np.vstack([B2, sp2.vec(p)])) == B2.shape[0]: lag = D2; break
            rec['new'].append(dict(poly=fmt(p, R['v']), degree=d, terms=len(p), sound=sound,
                                   in_base_closure_at=lag))
        print(json.dumps(rec, indent=1), flush=True); out.append(rec)
    json.dump(out, open(os.path.join(HERE, f'c3_witness_{tag}_D{D0}.json'), 'w'), indent=1)
