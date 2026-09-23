"""Component-corrected prediction for width-two product constraints in B = F_3[s_1..s_v]/(s_i^3) (the low-density model).
A circuit is a set S of constraints whose 2|S| forms span fewer than 2|S| dimensions while every proper nonempty subset
has full span.  Constraints are merged into components along circuits of at most three constraints.  A component C with
forms spanning d_C dimensions contributes the factor HS(B_C / (P_b : b in C)) / (1+t+t^2)^{d_C}, computed exactly in the
truncated ring B_C on its span; a component without a circuit is a single constraint with factor 1 - t^4/(1+t+t^2)^2.
Corrected prediction: HS_B times the product of the factors, truncated at its first nonpositive coefficient.  Compares it
with the recorded Hilbert function H.  Usage: --inp products.json --out JSON"""
import itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
LD = os.path.join(HERE, '..', 'odd_prime_low_density_20260923')
a = dict(zip(sys.argv[1::2], sys.argv[2::2]))
sys.argv = [sys.argv[0], '--vs', '', '--Ms', '']
exec(open(os.path.join(LD, 'products.py')).read().split('res = []')[0])
def basis_coords(vecs):
    """Row-reduce vecs over F_3; return (basis rows, coordinates of each vec in that basis)."""
    V = np.array(vecs, dtype=np.int64) % 3; basis = []
    for x in V:
        r = x.copy()
        for b, pc in basis:
            if r[pc]: r = (r - r[pc] * b) % 3
        nz = np.nonzero(r)[0]
        if len(nz): r = (r * r[nz[0]]) % 3; basis.append((r, nz[0]))   # r[nz[0]] in {1,2} is its own inverse mod 3
    B = np.array([b for b, _ in basis]); d = len(basis)
    coords = []
    for x in V:   # solve x = c B over F_3 by brute force on small d
        for c in itertools.product(range(3), repeat=d):
            if ((np.array(c) @ B) % 3 == x).all(): coords.append(list(c)); break
    return d, coords
def series_mul(a, b, K): return [sum(a[i] * b[k - i] for i in range(k + 1)) for k in range(K + 1)]
def inv_pow(d, K):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(K + 1)]; out = [1] + [0] * K
    for _ in range(d): out = series_mul(out, inv, K)
    return out
out = []
for x in json.load(open(a['--inp'])):
    v, M, K = x['v'], x['M'], len(x['H']) - 1; forms = [np.array(f) for f in x['forms']]
    rk = lambda S: rank3([forms[2 * b] for b in S] + [forms[2 * b + 1] for b in S])
    circuits = [S for k in (2, 3) for S in itertools.combinations(range(M), k)
                if rk(S) < 2 * k and all(rk(T) == 2 * len(T) for j in range(1, k) for T in itertools.combinations(S, j))]
    parent = list(range(M))
    def find(i):
        while parent[i] != i: i = parent[i]
        return i
    for S in circuits:
        for b in S[1:]: parent[find(b)] = find(S[0])
    comps = {}
    for b in range(M): comps.setdefault(find(b), []).append(b)
    Bser, _ = series_W(v, 0, K); W = Bser[:]; cinfo = []
    for C in comps.values():
        d, coords = basis_coords([forms[2 * b] for b in C] + [forms[2 * b + 1] for b in C])
        P = []
        for i, b in enumerate(C):
            m1, m2 = coords[i], coords[len(C) + i]
            P.append(polymul(polymul(lin(m1), lin(m1)), polymul(lin(m2), lin(m2))))
        HC = hilbert(d, P, K, [mons(d, k) for k in range(K + 1)])
        fac = series_mul(HC, inv_pow(d, K), K); W = series_mul(W, fac, K); cinfo.append(dict(constraints=C, span=d, H=HC))
    T = truncated(W); mism = [k for k in range(K + 1) if x['H'][k] != T[k]]
    pos = next((k for k, w in enumerate(W) if w <= 0), K + 1)   # corrected prediction positive below this degree
    rec = dict(v=v, M=M, trial=x['trial'], H=x['H'], W_old=x['W'], first_defect_old=x['first_defect'], circuits=[list(S) for S in circuits],
               components=cinfo, n_components=len(comps), W_corrected=W, T_corrected=T, mismatch_degrees=mism, positive_through=pos - 1)
    out.append(rec)
    if x['first_defect'] is not None or mism:
        print(v, M, x['trial'], 'old defect', x['first_defect'], 'circuits', rec['circuits'], 'comps', len(comps), 'mismatch', mism, flush=True)
json.dump(out, open(a['--out'], 'w'), indent=1, default=int)
tested = [r for r in out if r['n_components'] >= 2]
print('instances', len(out), 'with >=2 components', len(tested), 'old defects among them', sum(r['first_defect_old'] is not None for r in tested),
      'mismatches after correction', sum(bool(r['mismatch_degrees']) for r in tested))
