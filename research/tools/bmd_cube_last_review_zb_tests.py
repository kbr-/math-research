"""Route review bmd-20261004-zb cheap tests, from saved outputs only.
(1) Kummer transition scale: at the far-ring edge roots (|r| >= 5, bmd-20261004-za), zeta = N/|r| (N = R_e + 7/2)
against 4e, the largest mixed-row parameter scale; a transition-zone law zeta ~ c e predicts a constant zeta/(4e).
(2) Stokes inflation: Spearman rank correlation between log m (normalized |T'|) and |zeta| over all edge roots
(both sizes pooled per e); the Stokes picture predicts stronger cancellation (smaller m) at smaller |zeta|."""
import re, math
def rows(e):
    txt = open('research/results/bmd-20261004-za/edge-margin-e%d.txt' % e).read().split(']: ')[1]
    out = []
    for s in re.findall(r'\[([^\[\]]+)\]', txt):
        v = [float(t.replace(' E', 'E')) for t in s.split(',')]
        if len(v) == 12 and v[0] == 1:
            out.append(v)
    return out
def ranks(a):
    o = sorted(range(len(a)), key=lambda i: a[i]); r = [0] * len(a)
    for k, i in enumerate(o): r[i] = k
    return r
for e in (2, 4):
    N = e * (2 * e - 1) + 3.5
    R = rows(e)
    far = [v for v in R if abs(complex(v[1], v[2])) >= 5]
    z = [N / abs(complex(v[1], v[2])) for v in far]
    print('e=%d N=%.1f far-ring zeta range %.2f..%.2f, zeta/(4e) %.3f..%.3f' % (e, N, min(z), max(z), min(z) / (4 * e), max(z) / (4 * e)))
    zs = [N / abs(complex(v[1], v[2])) for v in R]; lm = [math.log10(v[10]) for v in R]
    a, b = ranks(zs), ranks(lm); n = len(R)
    rho = 1 - 6 * sum((a[i] - b[i]) ** 2 for i in range(n)) / (n * (n * n - 1))
    print('  edge roots %d: Spearman(zeta, log10 m) = %.3f' % (n, rho))
