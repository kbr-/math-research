"""Exhaustive catalogue of small overlapping configurations in the low-density model B_d = F_3[s_1..s_d]/(s_i^3): k width-two
product constraints P_b = mu_b^2 nu_b^2 whose 2k forms span exactly d dimensions (each constraint's two forms independent).
Up to GL_d the first constraint is (e_1, e_2); the remaining 2k-2 forms run over the projective points of F_3^d (one
representative per pair +-v), which is exact because P_b depends on its forms only through their squares.  For each configuration the
Hilbert function of B_d/(P_b) through degree 2d is compared with the truncated independent prediction; distinct outcomes are
counted, both against the truncated prediction and against the untruncated one (H - W, the component's correction
when it sits inside a larger ring).  Cases: (k, d) = (2, 2), (2, 3), (3, 3).  Usage: --out JSON"""
import itertools, json, os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); LD = os.path.join(HERE, '..', 'odd_prime_low_density_20260923')
outp = sys.argv[sys.argv.index('--out') + 1]
sys.argv = [sys.argv[0], '--vs', '', '--Ms', '']
exec(open(os.path.join(LD, 'products.py')).read().split('res = []')[0])
out = {}
for k, d in [(2, 2), (2, 3), (3, 3)]:
    K = 2 * d; monc = [mons(d, j) for j in range(K + 1)]; _, W = series_W(d, k, K); T = truncated(W)
    vecs = [np.array(v) for v in itertools.product(range(3), repeat=d) if any(v) and next(x for x in v if x) == 1]
    e1, e2 = np.eye(d, dtype=int)[0], np.eye(d, dtype=int)[1]
    cnt = collections.Counter(); first = {}; total = 0
    for rest in itertools.product(vecs, repeat=2 * k - 2):
        forms = [e1, e2] + list(rest)
        if any(rank3([forms[2 * b], forms[2 * b + 1]]) < 2 for b in range(k)) or rank3(forms) != d: continue
        P = [polymul(polymul(lin(forms[2 * b]), lin(forms[2 * b])), polymul(lin(forms[2 * b + 1]), lin(forms[2 * b + 1]))) for b in range(k)]
        H = tuple(hilbert(d, P, K, monc)); ex = (tuple(h - t for h, t in zip(H, T)), tuple(h - w for h, w in zip(H, W))); cnt[ex] += 1; total += 1
        first.setdefault(ex, [f.tolist() for f in forms])
    out[f'k{k}_d{d}'] = dict(k=k, d=d, T=T, W=W, configurations=total,
                            outcomes=[dict(excess_truncated=list(e[0]), H_minus_W=list(e[1]), count=c, example=first[e]) for e, c in cnt.most_common()])
    print(k, d, 'configs', total, 'T', T, 'W', W, [(list(e[0]), list(e[1]), c) for e, c in cnt.most_common()], flush=True)
json.dump(out, open(outp, 'w'), indent=1)
