import itertools
from collections import defaultdict
# Symbolic check: coefficients w_d treated as independent symbols (index d).
def E(t, j, args, k, T=6):
    res = defaultdict(int)
    for ts in itertools.product(range(T), repeat=j):
        idx = k - 1 - t - sum(2 ** x for x in ts)
        if idx < 0:
            continue
        mon = defaultdict(int)
        for v, x in zip(args, ts):
            mon[v] += 2 ** x
        res[(tuple(sorted(mon.items())), idx)] ^= 1
    return {kk for kk, v in res.items() if v}

def mulY(s):
    out = set()
    for mon, idx in s:
        m = dict(mon); m['Y'] = m.get('Y', 0) + 1
        out.add((tuple(sorted(m.items())), idx))
    return out

ok = True
for k in range(1, 30):
    for t in range(0, 4):
        for j in range(2, 5):
            Z = ['Z%d' % i for i in range(3, j + 1)]
            L = E(t, j, ['Y', 'Y'] + Z, k)
            R = E(t, j - 1, ['Y'] + Z, k) ^ mulY(E(t + 1, j - 2, Z, k))
            if L != R:
                ok = False; print('fail', k, t, j)
print('recursion ok', ok)
