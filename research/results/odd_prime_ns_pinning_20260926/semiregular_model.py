"""Compare the pinned-design dimensions of ns_pins.c with the semi-regular model.

Model (pin semi-regularity over F_3): if R is the quotient of the multilinear ring by FPHP^m_n,
graded by degree with Hilbert function h_i, and y_k = L_k - q_k are generic pins, each of which
satisfies y^3 = y modulo Booleanity (so its leading form satisfies y^3 = 0), then the design space
of degree d after h pins has dimension
    D_d(h) = sum_{i <= d} [ H_R(z) (1 - z)^h (1 - z^3)^(-h) ]_i,
and a Nullstellensatz refutation of degree d appears exactly when this number is <= 0.
h_0..h_d are read from the h = 0 lines: D_1 = 1 + mn - m, D_2 from the degree-2 run of the same
board, D_d from the case itself.  Usage: semiregular_model.py series.jsonl > model_check.txt
"""
import json, sys
from math import comb

rows = [json.loads(l) for l in open(sys.argv[1]) if l.startswith('{')]
base = {(r['m'], r['n'], r['d']): r['design_dim'] for r in rows if r.get('h') == 0 and 'seed' not in r}

def design_dims(m, n, d):
    D = [1, 1 + m * n - m]
    for e in range(2, d + 1):
        D.append(base[(m, n, e)])
    return D[:d + 1]

def predict(hilb, d, h):
    # sum of the coefficients of H(z)(1-z)^h(1-z^3)^(-h) up to degree d
    a = [0] * (d + 1)
    for i in range(d + 1):
        a[i] = sum((-1) ** j * comb(h, j) * hilb[i - j] for j in range(min(i, h) + 1))
    tot = 0
    for k in range(0, d // 3 + 1):          # (1 - z^3)^(-h) = sum_k C(h+k-1, k) z^(3k)
        c = comb(h + k - 1, k) if h > 0 else int(k == 0)
        tot += c * sum(a[i] for i in range(0, d - 3 * k + 1))
    return tot

ok = True
for (m, n, d), D0 in sorted(base.items()):
    if any((m, n, e) not in base for e in range(2, d + 1)):
        continue
    Ds = design_dims(m, n, d)
    hilb = [Ds[0]] + [Ds[i] - Ds[i - 1] for i in range(1, d + 1)]
    seeds = sorted({r['seed'] for r in rows if (r['m'], r['n'], r['d']) == (m, n, d) and 'seed' in r})
    for s in seeds:
        obs = {r['h']: r['design_dim'] for r in rows if (r['m'], r['n'], r['d']) == (m, n, d) and r.get('seed') == s and not r.get('summary')}
        hstar = max(obs)
        pred_star = next(h for h in range(1, 10 ** 6) if predict(hilb, d, h) <= 0)
        assert predict(hilb, d, 0) == Ds[d]
        mism = [(h, obs[h], predict(hilb, d, h)) for h in sorted(obs) if h < hstar and obs[h] != predict(hilb, d, h)]
        line = dict(m=m, n=n, d=d, seed=s, hilbert=hilb, h_star=hstar, predicted_h_star=pred_star,
                    residual_at_refutation=obs[hstar], mismatches_before_refutation=mism)
        ok &= (hstar == pred_star and not mism)
        print(json.dumps(line))
print(json.dumps({"all_match": ok}))
