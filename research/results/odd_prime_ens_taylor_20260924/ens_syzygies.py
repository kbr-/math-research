"""Top syzygies of ENS companions in the free-span model T'' = F_3[y_1..y_d, r_1..r_H]/(cubes).

Tested statement (ENS Taylor condition): for generic forms l in W = span(y), the syzygies of degree s <= DMAX
of the companion tops t_{a,i} = l_{a,i}^2 rho_a, rho_a = sum_k r_{a,k} l_{a,k}^2 (blocks a, inputs i), are
spanned by T''-multiples of: Frobenius l_{a,i} e_{a,i} (deg 6); block Koszul l_{a,k}^2 e_{a,i} - l_{a,i}^2
e_{a,k} (deg 7); cross-block Koszul t_{b,j} e_{a,i} - t_{a,i} e_{b,j} (deg 10); P-Frobenius rho_a^2 e_{a,i}
(deg 11). Each lifts exactly in the homogenized base (u^3 = u z^2, exact Koszul identities, P^3 = z^6 P), so
spanning would give an ENS Taylor-glue condition. Reports, per degree s, dim of the syzygy module and of the
natural span; a positive gap is an extra syzygy. Sign conventions do not affect spans.
Forms are independent within each block (asserted); across blocks they are random, so dependence is allowed.
Usage: python3 ens_syzygies.py OUT.json d:h:blocks[,d:h:blocks...] DMAX"""
import itertools, json, sys, time
import numpy as np
sys.path.insert(0, 'research/tools')
from rank_modp import rank_mod_p

def monos(nv, k):
    out = []
    def rec(i, left, cur):
        if i == nv:
            if left == 0: out.append(tuple(cur))
            return
        for e in range(min(2, left) + 1):
            cur.append(e); rec(i + 1, left - e, cur); cur.pop()
    rec(0, k, []); return out

def mul(a, b):
    out = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            e = tuple(x + y for x, y in zip(ea, eb))
            if max(e) <= 2: out[e] = (out.get(e, 0) + ca * cb) % 3
    return {e: c for e, c in out.items() if c}

def add(a, b, s=1):
    out = dict(a)
    for e, c in b.items(): out[e] = (out.get(e, 0) + s * c) % 3
    return {e: c for e, c in out.items() if c}

def case(d, h, blocks, dmax, rng):
    nv = d + h * blocks
    def var(k): e = [0] * nv; e[k] = 1; return {tuple(e): 1}
    forms = []; tops = []; rhos = []
    for a in range(blocks):
        ls = []
        while True:                                  # hypothesis: linear parts independent within each block
            C = rng.integers(0, 3, (h, d))
            if rank_mod_p([{k: int(C[i][k]) for k in range(d) if C[i][k]} for i in range(h)], d, 3) == h: break
        for i in range(h):
            c = C[i]
            l = {}
            for k in range(d):
                if c[k]: l = add(l, {tuple(1 if j == k else 0 for j in range(nv)): int(c[k])})
            ls.append(l)
        rho = {}
        for k in range(h): rho = add(rho, mul(var(d + a * h + k), mul(ls[k], ls[k])))
        forms.append(ls); rhos.append(rho)
        for i in range(h): tops.append(((a, i), mul(mul(ls[i], ls[i]), rho)))
    T = len(tops); idx = {key: n for n, (key, _) in enumerate(tops)}
    res = []
    for s in range(6, dmax + 1):
        dom = monos(nv, s - 5); tgt = monos(nv, s)
        if not dom or not tgt: continue
        di = {m: n for n, m in enumerate(dom)}; ti = {m: n for n, m in enumerate(tgt)}; nd = len(dom)
        rows = []
        for n, (_, t) in enumerate(tops):
            for m in dom:
                p = mul({m: 1}, t); rows.append({ti[e]: c for e, c in p.items()})
        rk = rank_mod_p(rows, len(tgt), 3); syz = T * nd - rk
        gens = []                                   # natural generators as vectors over (top index, coefficient)
        for a in range(blocks):
            for i in range(h):
                gens.append((6, {idx[(a, i)]: forms[a][i]}))
                gens.append((11, {idx[(a, i)]: mul(rhos[a], rhos[a])}))
                for k in range(i + 1, h):
                    gens.append((7, {idx[(a, i)]: mul(forms[a][k], forms[a][k]),
                                     idx[(a, k)]: {e: (-c) % 3 for e, c in mul(forms[a][i], forms[a][i]).items()}}))
        for (ka, ta), (kb, tb) in itertools.combinations(tops, 2):
            if ka[0] != kb[0]:
                gens.append((10, {idx[ka]: tb, idx[kb]: {e: (-c) % 3 for e, c in ta.items()}}))
        nat = []
        for deg, g in gens:
            if deg > s: continue
            for m in monos(nv, s - deg):
                row = {}
                for n, coef in g.items():
                    for e, c in mul({m: 1}, coef).items():
                        if e in di:
                            k = n * nd + di[e]; row[k] = (row.get(k, 0) + c) % 3
                row = {k: v for k, v in row.items() if v}
                if row: nat.append(row)
        nr = rank_mod_p(nat, T * nd, 3) if nat else 0
        res.append({'s': s, 'syzygies': syz, 'natural_span': nr, 'extra': syz - nr})
    return res

def main():
    out = {'cases': []}; dmax = int(sys.argv[3]); t0 = time.time()
    for spec in sys.argv[2].split(','):
        d, h, b = map(int, spec.split(':')); rng = np.random.default_rng(31 * d + 7 * h + b)
        t1 = time.time(); r = case(d, h, b, dmax, rng)
        rec = {'d': d, 'h': h, 'blocks': b, 'degrees': r, 'seconds': round(time.time() - t1, 1)}
        out['cases'].append(rec); print(json.dumps(rec), flush=True)
    out['seconds'] = round(time.time() - t0, 1); json.dump(out, open(sys.argv[1], 'w'), indent=1)

if __name__ == '__main__':
    main()
