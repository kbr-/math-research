"""Edge review (bmd-20261004-x): classify saved last-step roots (third/largest <= 1e-3 is balanced)
and print |r|, |r(1+r)|, |N/r| (N = R_e + 7/2) and log|t| ranges; reads research/results/bmd-20261004-t."""
import re, sys, math
def parse(path):
    txt = open(path).read()
    real = int(re.search(r'real roots skipped: (\d+)', txt).group(1))
    body = txt.split('Im r]: ')[1]
    nums = re.findall(r'\[([^\[\]]+)\]', body)
    rows = []
    for s in nums:
        v = [float(t.replace(' E', 'E')) for t in s.split(',')]
        if len(v) == 8: rows.append(v)
    return real, rows
for path, N in [('research/results/bmd-20261004-t/x-sector-all-e2.txt', 9.5),
                ('research/results/bmd-20261004-t/x-sector-all-e4-guarded.txt', 31.5)]:
    real, rows = parse(path)
    bal = [r for r in rows if r[3] <= 1e-3]
    unb = [r for r in rows if r[3] > 1e-3]
    def ab(r): z = complex(r[6], r[7]); return abs(z), abs(z*(1+z)), abs(N/z), r[0]
    print(path, 'real', real, 'sampled', len(rows), 'balanced', len(bal), 'unbalanced', len(unb))
    for name, S in [('bal', bal), ('unb', unb)]:
        if not S: continue
        a = [ab(r) for r in S]
        for k, lab in enumerate(['|r|', '|r(1+r)|', '|N/r|', 'log|t|']):
            print(' ', name, lab, round(min(x[k] for x in a), 3), round(max(x[k] for x in a), 3))
    print('  unbalanced (Re r, Im r>0, |r|, |r(1+r)|, log|t|):')
    for r in sorted(unb, key=lambda r: abs(complex(r[6], r[7]))):
        if r[7] > 0:
            z = complex(r[6], r[7]); print('   ', round(r[6], 2), round(r[7], 2), round(abs(z), 2), round(abs(z*(1+z)), 2), round(r[0], 3))
