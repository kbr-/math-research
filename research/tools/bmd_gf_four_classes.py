"""Representatives of 2-dim F_2-subspaces of GF(2^a) by the scaling invariant c1^3/c0^2 up to Frobenius.

Every such subspace scales to S = {0,1,u,u+1}, with L(x) = x^4 + (u^2+u+1) x^2 + (u^2+u) x.  Output lines:
the least Frobenius conjugate of the invariant (0 means a scaled F_4), then S.
Usage: bmd_gf_four_classes.py a poly   (e.g. 6 67 for GF(64) = F_2[x]/(x^6+x+1))
"""
import sys
a, poly = int(sys.argv[1]), int(sys.argv[2]); Q = 1 << a
def mul(x, y):
    r = 0
    while y:
        if y & 1: r ^= x
        y >>= 1; x <<= 1
        if x & Q: x ^= poly
    return r
def pw(x, e):
    r = 1
    for _ in range(e): r = mul(r, x)
    return r
reps = {}
for u in range(2, Q):
    S = [0, 1, u, u ^ 1]
    c0 = mul(u, u ^ 1)
    c1 = mul(u, u) ^ u ^ 1
    j = mul(pw(c1, 3), pw(pw(c0, 2), Q - 2))
    orb = min(pw(j, 1 << i) for i in range(a))
    reps.setdefault(orb, S)
for j, S in sorted(reps.items()):
    print(j, ' '.join(map(str, S)))
