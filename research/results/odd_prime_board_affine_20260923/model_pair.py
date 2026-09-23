"""Column-subalgebra model for pairs of column-type forms: Hilbert function of R/(l_1, l_2), R = F_3[t_1..t_n]/(t_j^2, sum t_j),
against HS_R/(1+t+t^2)^2 truncated; also every single F_3-combination against HS_R/(1+t+t^2).  Reuses model_ring.hf.
Usage: --n --pairs 'phi1|phi2;...' --out"""
import json, os, sys, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
args = dict(zip(sys.argv[1::2], sys.argv[2::2])); n = int(args['--n'])
sys.argv = [sys.argv[0], '--n', str(n), '--phis', '0']
src = open(os.path.join(HERE, 'model_ring.py')).read().split('out = []')[0]; exec(src)
def trunc(H, r):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(n + 1)]; c = [1] + [0] * n
    for _ in range(r): c = [sum(c[i] * inv[k - i] for i in range(k + 1)) for k in range(n + 1)]
    W = [sum(H[i] * c[k - i] for i in range(k + 1)) for k in range(n + 1)]; out = []; dead = False
    for w in W: dead = dead or w <= 0; out.append(0 if dead else w)
    return out
res = []; HR = hf([[1] * n])
for s in args['--pairs'].split(';'):
    p1, p2 = ([int(x) for x in t.split(',')] for t in s.split('|'))
    H = hf([[1] * n, p1, p2]); T = trunc(HR, 2)
    singles = []
    for a, b in [(1, 0), (0, 1), (1, 1), (1, 2)]:
        ph = [(a * x + b * y) % 3 for x, y in zip(p1, p2)]; Hs = hf([[1] * n, ph]); Ts = trunc(HR, 1)
        singles.append(dict(coeffs=[a, b], excess=[h - t for h, t in zip(Hs, Ts)]))
    res.append(dict(phi1=p1, phi2=p2, H=H, T=T, excess=[h - t for h, t in zip(H, T)], singles=singles)); print(res[-1], flush=True)
json.dump(dict(n=n, HR=HR, results=res), open(args['--out'], 'w'), indent=1)
