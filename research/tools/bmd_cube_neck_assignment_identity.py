"""Check of the closed form of the neck assignment count (cycle bmd-20260930-zzy).

E_{l,w}(c) (assignE of bmd_cube_neck_separation.gp): sort the multiset {0,...,w-1}, each value l times;
top = the c largest entries in ascending order; E = sum_{i=1..c} max(0, i - 1 - top[i]).
Claims, for l >= 2, w >= 1, w <= c <= lw, d = c - w = (l-1) a + b with 0 <= b < l-1:
  (1) 2E = d(d+1) + 2ad - (l-1)a(a+1);
  (2) 2E = c^2 + sum k_i^2 - l w^2, (k_i) the most balanced split of lw - c into l-1 parts.
Exhaustive over 2 <= l <= 30, 1 <= w <= 30, all c; prints the number of windows and any failure.
"""
def assignE(l, w, c):
    rows = sorted(v for v in range(w) for _ in range(l))
    top = rows[len(rows) - c:]
    return sum(max(0, i - 1 - top[i - 1]) for i in range(1, c + 1))

def balanced(m, parts):
    q, r = divmod(m, parts)
    return [q + 1] * r + [q] * (parts - r)

n = bad = 0
for l in range(2, 31):
    for w in range(1, 31):
        for c in range(w, l * w + 1):
            E = assignE(l, w, c)
            d = c - w
            a, b = divmod(d, l - 1)
            f1 = d * (d + 1) + 2 * a * d - (l - 1) * a * (a + 1)
            f2 = c * c + sum(k * k for k in balanced(l * w - c, l - 1)) - l * w * w
            n += 1
            if not (2 * E == f1 == f2):
                bad += 1
                print("failure", l, w, c, 2 * E, f1, f2)
print("windows checked:", n, "failures:", bad)
