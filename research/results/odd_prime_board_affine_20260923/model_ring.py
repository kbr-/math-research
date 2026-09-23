"""Model for column-type forms: R = F_3[t_1..t_n]/(t_j^2, z), z = sum_j t_j (the column-sum subalgebra modulo the row sum).
For a hole function phi, compares the Hilbert function of R/(l_phi) with HS_R/(1+t+t^2) truncated at its first nonpositive
coefficient, and reports the first excess degree; c = n - (largest multiplicity of a value of phi).
Usage: --n --phis 'a,b,c;...'"""
import argparse, itertools, json, os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int); ap.add_argument('--phis'); ap.add_argument('--out'); opt = ap.parse_args(); n = opt.n
def hf(lins):
    """Hilbert function of F_3[t]/(t_j^2, lins) (lins: list of coefficient vectors), via subsets."""
    H = []
    for k in range(n + 1):
        Bk = list(itertools.combinations(range(n), k)); idx = {b: i for i, b in enumerate(Bk)}
        if k == 0: H.append(1); continue
        rows = []
        for S in itertools.combinations(range(n), k - 1):
            for lv in lins:
                r = np.zeros(len(Bk), dtype=np.uint8)
                for j in range(n):
                    if j not in S and lv[j] % 3: r[idx[tuple(sorted(S + (j,)))]] = (r[idx[tuple(sorted(S + (j,)))]] + lv[j]) % 3
                rows.append(r)
        H.append(len(Bk) - (gf3.rank(np.array(rows)) if rows else 0))
    return H
out = []
for s in opt.phis.split(';'):
    phi = [int(x) for x in s.split(',')]; c = n - max(collections.Counter(phi).values())
    HR = hf([[1] * n]); HQ = hf([[1] * n, phi])
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(n + 1)]
    W = [sum(HR[i] * inv[k - i] for i in range(k + 1)) for k in range(n + 1)]; T = []; dead = False
    for w in W: dead = dead or w <= 0; T.append(0 if dead else w)
    first = next((k for k in range(n + 1) if HQ[k] != T[k]), None)
    row = dict(n=n, phi=phi, c=c, ceil_c_half=-(-c // 2), H_R=HR, H_quot=HQ, T=T, first_excess=first); out.append(row); print(row)
if opt.out: json.dump(out, open(opt.out, 'w'), indent=1)
