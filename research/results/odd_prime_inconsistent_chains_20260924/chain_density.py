"""Allowed fraction of a chain's constraints in form-value space F_3^{L+1} (the forms' values are close to uniform on the
slice for dense random forms): clause i allows f_{i-1} = u or f_i = v, with (u, v) = (0, 1) (inconsistent links) or
(0, 0) (consistent).  Exact count by dynamic programming over the chain.  Usage: python3 chain_density.py L [...]"""
import sys
for L in map(int, sys.argv[1:]):
    for kind, (u, v) in (('inc', (0, 1)), ('con', (0, 0))):
        cnt = {x: 1 for x in range(3)}                     # value of f_0
        for i in range(L):                                  # add f_{i+1} and clause i+1
            new = {y: 0 for y in range(3)}
            for x, c in cnt.items():
                for y in range(3):
                    if x == u or y == v: new[y] += c
            cnt = new
        tot = sum(cnt.values()); print(L, kind, tot, '/', 3 ** (L + 1), '=', round(tot / 3 ** (L + 1), 6))
