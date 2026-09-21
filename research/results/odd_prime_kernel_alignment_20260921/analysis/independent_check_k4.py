# Independent recomputation of dim(W cap J_4) in the full graded space A_4 (all C(s,4) monomials).
import itertools, zlib, json, time
import numpy as np
N, d, k = 8, 4, 4
rng = np.random.default_rng(5)
nb = [[int(x) for x in rng.choice(N, size=d, replace=False)] for _ in range(N + 1)]
dist = [r[0] for r in nb]
cells = [(i, h) for i in range(N + 1) for h in nb[i][1:]]
s = len(cells)
rng = np.random.default_rng(zlib.crc32(b'N8d4k4|4|square|18'))
F = [rng.integers(0, 3, size=s) for _ in range(4)]
R = json.load(open('research/results/odd_prime_kernel_alignment_20260921/alignment_k4many.json'))
row = [r for r in R['rows'] if r['config'] == 'N8d4k4' and r['h'] == 4 and r['kind'] == 'square' and r['trial'] == 18][0]
assert (np.array(F) == np.array(row['forms'])).all()
A4 = list(itertools.combinations(range(s), 4)); col = {m: j for j, m in enumerate(A4)}
A2 = list(itertools.combinations(range(s), 2))
n = len(A4)
# old degree-two top forms, as dicts {(u,v): coeff}, u<v, over the full ring A
rowc = {i: [u for u in range(s) if cells[u][0] == i] for i in range(N + 1)}
T = []
for u, v in A2:
    if cells[u][0] == cells[v][0] or cells[u][1] == cells[v][1]: T.append({(u, v): 1})
for u in range(s):   # x_{i,p_i} x_u with p_i = hole(u), x_{i,p_i} = 1 - S_i  -> top form -y_u S_i
    for i in range(N + 1):
        if i != cells[u][0] and dist[i] == cells[u][1]:
            T.append({tuple(sorted((u, v))): 2 for v in rowc[i]})
for i in range(N + 1):
    for j in range(i + 1, N + 1):
        if dist[i] == dist[j]:
            T.append({tuple(sorted((a, b))): 1 for a in rowc[i] for b in rowc[j]})
# (same row distinguished x nondistinguished: (1-S_i) y_u top form = -sum_{v in row, v != u} y_u y_v, in span of same-row monomials)
SQ = [{(u, v): int(2 * f[u] * f[v] % 3) for u, v in A2 if f[u] * f[v] % 3} for f in F]
def mult(forms):
    out = []
    for q in forms:
        for m in A2:
            r = {}
            for (u, v), c in q.items():
                if u in m or v in m: continue
                key = col[tuple(sorted((u, v) + m))]
                r[key] = (r.get(key, 0) + c) % 3
            r = {a: b for a, b in r.items() if b}
            if r: out.append(r)
    return out
TR, SR = mult(T), mult(SQ)
good = []
for m in A4:
    rs = [cells[u][0] for u in m]; hs = [cells[u][1] for u in m] + [dist[x] for x in rs]
    if len(set(rs)) == 4 and len(set(hs)) == 8: good.append(m)
WR = [{col[m]: 1} for m in good]
print('s', s, 'n', n, 'T rows', len(TR), 'square rows', len(SR), 'good', len(good), flush=True)

def dense(rows):
    M = np.zeros((len(rows), n), dtype=np.uint8)
    for a, r in enumerate(rows):
        for j, c in r.items(): M[a, j] = c
    return M

class Ech:
    """Exact reduced row echelon basis mod 3 over all n columns (plain Gaussian elimination)."""
    def __init__(self): self.E = np.zeros((0, n), dtype=np.uint8); self.piv = []
    def add(self, B):
        B = B.astype(np.int64) % 3
        if self.piv: B = (B - B[:, self.piv] @ self.E.astype(np.int64)) % 3
        B = B.astype(np.uint8)
        newE, newp = [], []
        B = B[B.any(axis=1)]
        while B.shape[0]:
            r0 = B[0]; c = int(np.nonzero(r0)[0][0])
            r0 = (r0 * r0[c]) % 3  # inverse of 1 is 1, of 2 is 2
            nz = np.nonzero(B[1:, c])[0] + 1
            if len(nz): B[nz] = (B[nz] + (3 - B[nz, c])[:, None] * r0[None, :]) % 3
            # also clear column c in already-found new rows
            for t in range(len(newE)):
                if newE[t][c]: newE[t] = (newE[t] + (3 - newE[t][c]) * r0) % 3
            newE.append(r0); newp.append(c)
            B = B[1:]; B = B[B.any(axis=1)]
        if newE:
            NE = np.array(newE, dtype=np.uint8)
            if self.piv:
                self.E = ((self.E.astype(np.int64) - self.E[:, newp].astype(np.int64) @ NE.astype(np.int64)) % 3).astype(np.uint8)
            self.E = np.vstack([self.E, NE]); self.piv += newp
        return len(newp)
    def rank(self): return len(self.piv)
    def copy(self):
        e = Ech(); e.E = self.E.copy(); e.piv = list(self.piv); return e

t0 = time.time()
ET = Ech()
# singleton (monomial) rows first: exact, cheap
mono = sorted({next(iter(r)) for r in TR if len(r) == 1})
ET.E = np.zeros((len(mono), n), dtype=np.uint8); ET.E[np.arange(len(mono)), mono] = 1; ET.piv = list(mono)
rest = [r for r in TR if len(r) > 1]
# reduce rest by monomials: zero those columns (exact elimination by unit rows)
monoset = set(mono)
rest = [{a: b for a, b in r.items() if a not in monoset} for r in rest]
rest = [r for r in rest if r]
# dense elimination only on remaining columns for speed, then embed
cols = sorted(set(range(n)) - monoset); cidx = {c: j for j, c in enumerate(cols)}
nn = len(cols); print('monomial pivots', len(mono), 'remaining cols', nn, 'rest rows', len(rest), flush=True)
def sub(rows):
    M = np.zeros((len(rows), nn), dtype=np.uint8)
    for a, r in enumerate(rows):
        for j, c in r.items():
            if j in cidx: M[a, cidx[j]] = c
    return M
n_saved = n; n = nn
ETs = Ech()
for b in range(0, len(rest), 400): ETs.add(sub(rest[b:b + 400]))
rT = len(mono) + ETs.rank(); print('rank T', rT, 'time', round(time.time() - t0), flush=True)
EW = ETs.copy(); rTW = len(mono) + ETs.rank() + EW.add(sub(WR))
EJ = ETs.copy()
for b in range(0, len(SR), 400): EJ.add(sub(SR[b:b + 400]))
rJ = len(mono) + EJ.rank()
rJW = rJ + EJ.copy().add(sub(WR))
dWT = len(good) + rT - rTW; dWJ = len(good) + rJ - rJW
q = n_saved - rT; wp = len(good) - dWT; beta = rJ - rT
print(dict(dimA4=n_saved, rankT=rT, q=q, dim_W=len(good), dim_W_cap_T=dWT, w_image=wp, rankJ=rJ, beta=beta,
           dim_W_cap_J=dWJ, image_intersection=dWJ - dWT, predicted=max(0, wp + beta - q),
           reported=dict(beta=row['beta'], actual=row['actual'], predicted=row['predicted'])), flush=True)
print('time', round(time.time() - t0))
