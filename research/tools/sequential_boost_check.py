#!/usr/bin/env python3
"""Check of the sequential boost bound (Lemma N, cycle 226) on random affine subspaces.

Labels are l-bit strings, n = 2^l, n rows. S_0 = bijections, S_1 = labelings with exactly one
colliding pair. For a random affine subspace H (forms supported on a random set of tau rows,
codimension s) the exact boosts P(H | S_j) / 2^(-s) are compared with
  min over orderings of the touched rows of  prod_{pivot positions i} C_j / (n - i + 1),
C_0 = n, C_1 = n + 3.  Exact enumeration of S_0 and S_1; no sampling of points.
"""
import argparse, itertools, json, random
import numpy as np

def rank(vs):
    vs = list(vs); r = 0
    while vs:
        v = vs.pop()
        if v == 0: continue
        r += 1; hb = v.bit_length() - 1
        vs = [w ^ v if (w >> hb) & 1 else w for w in vs]
    return r

def parity(a):
    a = a.copy()
    for sh in (32, 16, 8, 4, 2, 1): a ^= a >> sh
    return a & 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--l', type=int, required=True); ap.add_argument('--trials', type=int, default=300)
    ap.add_argument('--maxtau', type=int, default=5); ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--out', required=True)
    a = ap.parse_args(); l = a.l; n = 1 << l; rng = random.Random(a.seed)
    perms = np.array(list(itertools.permutations(range(n))), dtype=np.int64)
    sh = np.array([l * i for i in range(n)], dtype=np.int64)
    S0 = (perms << sh).sum(axis=1)
    S1 = []
    for i in range(n):            # row i copies the label of row j (j != i); the label of row i is dropped
        for j in range(n):
            if i == j: continue
            q = perms.copy(); q[:, i] = q[:, j]; S1.append((q << sh).sum(axis=1))
    S1 = np.unique(np.concatenate(S1))   # every element arises twice (either label of the pair missing)
    assert len(S1) == len(S0) * n * (n - 1) // 2, (len(S1), len(S0))
    worst = {0: 0.0, 1: 0.0}; rows_out = []
    for t in range(a.trials):
        tau = rng.randint(1, min(a.maxtau, n)); T = rng.sample(range(n), tau)
        s = rng.randint(1, min(tau * l, 8))
        rowmask = sum(((1 << l) - 1) << (l * i) for i in T)
        forms = []
        while rank(forms) < s:
            f = rng.getrandbits(n * l) & rowmask
            if rank(forms + [f]) > rank(forms): forms.append(f)
        consts = [rng.getrandbits(1) for _ in forms]
        touched = [i for i in range(n) if any((f >> (l * i)) & ((1 << l) - 1) for f in forms)]
        best = {0: float('inf'), 1: float('inf')}
        for order in itertools.permutations(touched):
            b0 = b1 = 1.0; prev = 0
            for pos in range(1, len(order) + 1):
                later = sum(((1 << l) - 1) << (l * i) for i in order[pos:])
                dim_i = s - rank([f & later for f in forms])   # forms supported on the first pos rows
                if dim_i > prev: b0 *= n / (n - pos + 1); b1 *= (n + 3) / (n - pos + 1)
                prev = dim_i
            best[0] = min(best[0], b0); best[1] = min(best[1], b1)
        rec = {'tau': len(touched), 's': s}
        for j, S in ((0, S0), (1, S1)):
            ok = np.ones(len(S), dtype=bool)
            for f, c in zip(forms, consts): ok &= parity(S & np.int64(f)) == c
            boost = ok.mean() * 2 ** s
            rec[f'boost{j}'] = boost; rec[f'bound{j}'] = best[j]
            assert boost <= best[j] * (1 + 1e-9), (rec, forms, consts)
            worst[j] = max(worst[j], boost / best[j])
        rows_out.append(rec)
    json.dump({'l': l, 'trials': a.trials, 'violations': 0, 'largest_ratio_boost_over_bound': worst,
               'records': rows_out}, open(a.out, 'w'), indent=1)
    print('l', l, 'trials', a.trials, 'violations 0; largest boost/bound', worst)

if __name__ == '__main__': main()
