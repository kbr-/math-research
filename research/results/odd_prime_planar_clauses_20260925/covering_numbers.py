"""Covering numbers of the hub active sets of the clause families in clause_locality*.sing and clause_points.sing.

For a clause block b whose S-forms are affine forms in the hub coordinates, its active set is
A_b = {v in F_3^d : every S-form of b is nonzero at v}.  For O a set of blocks, V_O = F_3^d minus the union of A_b.
The covering number h(F) is the largest, over O, of the least |O'| with O' a subset of O and V_O' = V_O (the least
subfamily with the same union).  The clause hub criterion implies the family is h(F)-local.
This script prints h(F) next to the least t measured by the Singular scripts (read from their .out files).
"""
import itertools, re, sys, os

def pts(d):
    return list(itertools.product(range(3), repeat=d))

def active(forms, d):
    # forms: list of (coefficient vector, constant); value = sum c_i v_i + const mod 3
    return frozenset(v for v in pts(d) if all((sum(c * x for c, x in zip(co, v)) + k) % 3 != 0 for co, k in forms))

def covering(A):
    m = len(A); best = 0
    for r in range(1, m + 1):
        for O in itertools.combinations(range(m), r):
            U = frozenset().union(*(A[i] for i in O))
            need = next(s for s in range(0, r + 1) for Op in itertools.combinations(O, s)
                        if frozenset().union(*(A[i] for i in Op)) == U) if U else 0
            best = max(best, need)
    return best

def L(s, names):
    # parse a Singular affine form like "x - y + 1" over the given variable names
    s = s.replace(' ', '')
    if s[0] not in '+-': s = '+' + s
    co = [0] * len(names); k = 0
    for sign, term in re.findall(r'([+-])([^+-]+)', s):
        sg = 1 if sign == '+' else -1
        if term in names: co[names.index(term)] += sg
        else: k += sg * int(term)
    return (tuple(c % 3 for c in co), k % 3)

def fam(spec, names):
    return [[L(f, names) for f in blk] for blk in spec]

P = ['x', 'y']; H = ['x', 'y', 'v']; D = ['x', 'y', 'v', 's']
F = {
 'P4': (fam([['x','y'],['x+y','x-y'],['x','x+y'],['y','x-y']], P), P),
 'P4w': (fam([['x','y'],['x+y','x-y'],['x','x+y'],['y','x-y']], P), P),
 'P6': (fam([['x','y'],['x+y','x-y'],['x','x+y'],['y','x-y'],['x','x-y'],['y','x+y']], P), P),
 'H3': (fam([['x','y'],['y','v'],['x+y','v'],['x-v','y+v'],['x+y+v','x-y'],['x','y+v'],['x-y+v','v-x'],['y-v','x+v']], H), H),
 'A1w': (fam([['x'],['x+1'],['y'],['x+y-1'],['x-y+1'],['y-1']], P), P),
 'A2w': (fam([['x','y+1'],['x+1','x-y'],['y','x+y-1'],['x+y+1','x-y+1'],['x-1','y-1'],['x-y','x+y']], P), P),
 'T3': (fam([['x','y','v'],['x+y','y+v','x-v'],['x+v','x-y','y-v'],['x+y+v','x-y+v','y'],['x-y-v','x+y','v'],['x','y-v','x+y+v'],['x+v','y','x-y-v']], H), H),
 'D4': (fam([['x','y'],['v','s'],['x+v','y+s'],['x-s','y+v'],['x+y+v','s-x'],['y-v','x+s'],['x+y+v+s','x-y'],['v-s+x','y+s']], D), D),
 'D4w3': (fam([['x','y','v'],['v','s','x+y'],['x+v','y+s','x-y'],['x-s','y+v','s'],['x+y+v','s-x','y'],['y-v','x+s','x+y+s']], D), D),
}
def ptf(a, b):
    return [f'x-{a}-1', f'x-{a}+1', f'y-{b}-1', f'y-{b}+1']
def ptfam(pl):
    out = []
    for a, b in pl:
        out.append([L(f.replace('--', '+').replace('-+', '-').replace('+-', '-'), P) for f in ptf(a, b)])
    return out
six = [(1,0),(1,1),(1,-1),(-1,0),(-1,1),(-1,-1)]
F['PT6'] = (ptfam(six), P)
F['PT8'] = (ptfam(six + [(0,1),(0,-1)]), P)

measured = {}
here = os.path.dirname(os.path.abspath(__file__))
for fn in ['clause_locality.out', 'clause_locality2.out', 'clause_points.out']:
    for line in open(os.path.join(here, fn)):
        m = re.match(r'(\w+): t = (\d+), .*lowest_fall=(-?\d+)', line)
        if m and m.group(3) == '-1':
            nm, t = m.group(1), int(m.group(2))
            measured[nm] = min(measured.get(nm, 99), t)
print('family  hub_dim  blocks  covering_number  least_local_t  active_set_sizes')
for nm, (fm, names) in F.items():
    A = [active(b, len(names)) for b in fm]
    print(f'{nm:6s}  {len(names):7d}  {len(A):6d}  {covering(A):15d}  {measured.get(nm, "?"):>13}  {[len(a) for a in A]}')
