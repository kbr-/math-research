"""Edge circle-ends check (bmd-20261004-z): for each non-balanced non-real last-step root, is its dominant adjacent
sector pair the pair whose balanced roots lie on the same side of |t| = 1?  Reads research/results/bmd-20261004-t."""
import re
for path in ['research/results/bmd-20261004-t/x-sector-all-e2.txt','research/results/bmd-20261004-t/x-sector-all-e4-guarded.txt']:
    body = open(path).read().split('Im r]: ')[1]
    bal, edge = {}, []
    for s in re.findall(r'\[([^\[\]]+)\]', body):
        v = [float(t.replace(' E','E')) for t in s.split(',')]
        if len(v) != 8: continue
        pair = tuple(sorted((int(v[1]), int(v[2]))))
        if v[3] <= 1e-3:
            bal.setdefault(pair, []).append(v[0])
        elif v[7] > 0:
            edge.append((pair, v[0], v[6], v[7]))
    print(path[-14:], 'balanced: pair -> log|t| range', {p: (round(min(l), 2), round(max(l), 2), len(l)) for p, l in sorted(bal.items())})
    agree = 0; tot = 0
    for pair, lt, re_, im in edge:
        if pair in bal:
            tot += 1; side = max(bal[pair]) > 0 and min(bal[pair]) > 0
            sideneg = max(bal[pair]) < 0
            ok = (lt > 0 and side) or (lt < 0 and sideneg)
            agree += ok
            print('  edge', pair, 'log|t| %.3f' % lt, 'r=%.2f%+.2fi' % (re_, im), 'same side' if ok else 'OTHER side')
        else:
            print('  edge', pair, 'non-adjacent pair, r=%.2f%+.2fi' % (re_, im))
    print('  same side', agree, 'of', tot)
