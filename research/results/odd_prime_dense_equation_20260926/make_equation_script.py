#!/usr/bin/env python3
"""Generate one Singular script measuring refutation degrees of functional graph PHP plus one linear equation.

Tested statement (model case of the relative-review next step, 26 September 2026): adding one linear equation
L = 0 over F_3 that is far from additive does not lower the refutation degree of functional graph PHP, while
counting statistics (column total sum x - n) refute at degree 1. For each random bipartite graph (P pigeons,
H holes, each pigeon a uniform d-subset, every hole covered), the base system is Booleanity x^2-x, functionality
x_uv x_uv', collisions x_uv x_u'v and linear rows sum_v x_uv - 1 over F_3; variants add one equation:
coltotal (sum of all cells - H), additive (u_i + v_t + c, random), near-additive (additive plus two random cells),
dense (uniform random coefficients and constant), three samples each where random. For D = 1..Dmax the script
runs std with degBound = D (dp order) and records the least D whose truncated standard basis contains 1
(Groebner degree; by Clegg-Edmonds-Impagliazzo it equals the PC refutation degree for degree-compatible orders).
Usage: make_equation_script.py --out SCRIPT --meta META.json [--graphs 4] [--P 8] [--H 7] [--d 3] [--Dmax 5] [--seed S]
"""
import argparse, json
import numpy as np


def graph(rng, P, H, d):
    while True:
        nb = [sorted(rng.choice(H, size=d, replace=False).tolist()) for _ in range(P)]
        if len(set(h for N in nb for h in N)) == H:
            return nb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True); ap.add_argument('--meta', required=True)
    ap.add_argument('--graphs', type=int, default=4); ap.add_argument('--P', type=int, default=8)
    ap.add_argument('--H', type=int, default=7); ap.add_argument('--d', type=int, default=3)
    ap.add_argument('--Dmax', type=int, default=5); ap.add_argument('--seed', type=int, default=20260926)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    lines = ['option(redSB);', 'int D; int found;']
    meta = []
    for g in range(a.graphs):
        nb = graph(rng, a.P, a.H, a.d)
        cells = [(u, v) for u in range(a.P) for v in nb[u]]
        name = {c: f'x({i+1})' for i, c in enumerate(cells)}
        lines.append(f'ring r{g} = 3, (x(1..{len(cells)})), dp; ideal J;')
        base = [f'{name[c]}^2-{name[c]}' for c in cells]
        for u in range(a.P):
            base += [f'{name[(u,v)]}*{name[(u,w)]}' for i, v in enumerate(nb[u]) for w in nb[u][i+1:]]
            base.append('+'.join(name[(u, v)] for v in nb[u]) + '-1')
        for v in range(a.H):
            us = [u for u in range(a.P) if v in nb[u]]
            base += [f'{name[(u,v)]}*{name[(w,v)]}' for i, u in enumerate(us) for w in us[i+1:]]
        variants = [('base', None), ('coltotal', {c: 1 for c in cells} | {'const': -a.H})]
        for s in range(3):
            uu = rng.integers(0, 3, a.P); vv = rng.integers(0, 3, a.H); c0 = int(rng.integers(0, 3))
            add = {c: int((uu[c[0]] + vv[c[1]]) % 3) for c in cells}; add['const'] = c0
            variants.append((f'additive{s}', add))
            near = dict(add)
            for c in rng.choice(len(cells), size=2, replace=False):
                near[cells[c]] = int((near[cells[c]] + 1) % 3)
            variants.append((f'nearadditive{s}', near))
            dense = {c: int(rng.integers(0, 3)) for c in cells}; dense['const'] = int(rng.integers(0, 3))
            variants.append((f'dense{s}', dense))
        for vname, L in variants:
            eqs = list(base)
            if L is not None:
                terms = [f'{L[c]}*{name[c]}' for c in cells if L[c] % 3]
                eqs.append(('+'.join(terms) if terms else '0') + f'+({L["const"] % 3})')
            tag = f'g{g}_{vname}'
            meta.append({'graph': g, 'variant': vname, 'tag': tag})
            lines.append('ideal I = ' + ',\n  '.join(eqs) + ';')
            lines.append(f'found = 0; for (D = 1; D <= {a.Dmax} && found == 0; D++) {{ degBound = D; J = std(I); '
                         f'if (size(J) == 1 && J[1] == 1) {{ found = D; }} }}')
            lines.append(f'print("RESULT {tag} " + string(found));')
            lines.append('degBound = 0; kill I;')
        lines.append(f'kill r{g};')
    lines.append('quit;')
    open(a.out, 'w').write('\n'.join(lines) + '\n')
    json.dump({'params': vars(a), 'instances': meta}, open(a.meta, 'w'), indent=1)


if __name__ == '__main__':
    main()
