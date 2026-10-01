"""Root selection for the XEDGE mode (bmd-20261004-za): from the saved last-step sector classifications
(research/results/bmd-20261004-t), print a PARI list of [Re r, Im r, kind] for every unbalanced root with Im r > 0
(kind 1) and every fourth balanced root with Im r > 0 (kind 0).  Usage: python3 ... e2|e4."""
import re, sys
path = {'e2': 'research/results/bmd-20261004-t/x-sector-all-e2.txt',
        'e4': 'research/results/bmd-20261004-t/x-sector-all-e4-guarded.txt'}[sys.argv[1]]
body = open(path).read().split('Im r]: ')[1]
sel, nb = [], 0
for s in re.findall(r'\[([^\[\]]+)\]', body):
    v = [float(t.replace(' E', 'E')) for t in s.split(',')]
    if len(v) != 8 or v[7] <= 0:
        continue
    if v[3] > 1e-3:
        sel.append('[%.12g,%.12g,1]' % (v[6], v[7]))
    else:
        if nb % 4 == 0:
            sel.append('[%.12g,%.12g,0]' % (v[6], v[7]))
        nb += 1
print('[' + ','.join(sel) + ']')
