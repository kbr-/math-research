"""Diagonal defects of one form on the pattern algebra P(R,L), characteristic 3.
For l = sum c_x x with all c_x != 0 and u = sum nu_x c_x x, l^2 u = 2 sum_{faces F={x,y,z}} c_x c_y c_z (nu_x+nu_y+nu_z) F,
so the diagonal kernel is {nu : nu_x+nu_y+nu_z = 0 on every 3-face}.  Its dimension over F_3 is computed exactly
(compiled gf3 rank of the face-cell incidence matrix); dimension 1 (the constants, i.e. the Frobenius syzygy) means no
diagonal defect.  Usage: python3 diagonal_defect.py OUT.json"""
import itertools, json, os, sys
import numpy as np
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(RES, 'odd_prime_alignment_mechanism_20260922')); import gf3
PAT3 = {(0, 2, 3), (1, 0, 2), (1, 2, 0), (1, 2, 3)}
def faces3(R, L):
    out = []
    for rows in itertools.combinations(range(R), 3):
        for labs in itertools.permutations(range(L), 3):
            if any(labs[i] == 0 and labs[j] == 1 for i in range(3) for j in range(i + 1, 3)) or labs in PAT3: continue
            out.append([r * L + c for r, c in zip(rows, labs)])
    return np.array(out, dtype=np.int64)
res = []
for R in range(3, 10):
    for L in range(4, 9):
        F = faces3(R, L); A = np.zeros((len(F), R * L), dtype=np.uint8)
        A[np.repeat(np.arange(len(F)), 3), F.ravel()] = 1
        rk = int(gf3.rank(A)); res.append(dict(R=R, L=L, cells=R * L, faces=len(F), rank=rk, kernel_dim=R * L - rk))
print('R, L with kernel_dim != 1:', [(r['R'], r['L'], r['kernel_dim']) for r in res if r['kernel_dim'] != 1])
json.dump(res, open(sys.argv[1], 'w'), indent=1)
