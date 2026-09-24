import itertools, sys
# delta(n,k,l): least d with a polynomial of degree <= d over F_2, Hasse mult >= k at nonzero
# points of F_2^n and exactly l at origin.  dim W_d(>=l) > dim W_d(>=l+1).
def monos(n, d):
    out = []
    for tot in range(d + 1):
        for c in itertools.combinations_with_replacement(range(n), tot):
            a = [0] * n
            for i in c: a[i] += 1
            out.append(tuple(a))
    return out

def rank(rows):
    piv = {}
    r = 0
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in piv: v ^= piv[h]
            else: piv[h] = v; r += 1; break
    return r

def odd_binom(a, b):
    return b <= a and (a & b) == b

def rows_for(n, d, k, l, mons, idx):
    rows = []
    pts = list(itertools.product((0, 1), repeat=n))
    for a in pts:
        need = l if not any(a) else k
        for beta in monos(n, need - 1) if need > 0 else []:
            v = 0
            for al in mons:
                good = True
                for i in range(n):
                    if a[i] == 0:
                        if al[i] != beta[i]: good = False; break
                    else:
                        if not odd_binom(al[i], beta[i]): good = False; break
                if good: v |= 1 << idx[al]
            rows.append(v)
    return rows

def delta(n, k, l):
    d = 0
    while True:
        mons = monos(n, d); idx = {m: i for i, m in enumerate(mons)}
        r1 = rank(rows_for(n, d, k, l, mons, idx))
        r2 = rank(rows_for(n, d, k, l + 1, mons, idx))
        if r2 > r1: return d
        d += 1

def Phi(n, k, l):
    return n + 2 * l + sum((k - l - 1) // 2 ** j for j in range(n))

n = int(sys.argv[1]); K = int(sys.argv[2])
bad = 0; tested = 0
for k in range(1, K + 1):
    for l in range(k):
        if n >= 3 and k - l <= 2 ** n: continue
        dl = delta(n, k, l); p = Phi(n, k, l); tested += 1
        flag = '' if dl == p else ' MISMATCH'
        if dl != p: bad += 1
        print(n, k, l, 'k-l>2^n' if k - l > 2 ** n else '', dl, p, flag, flush=True)
print('tested', tested, 'mismatches', bad)
