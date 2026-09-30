"""Divided-difference Hall bound for the peeling neck windows (30 September 2026; cycle bmd-20260930-zg).

E'_(l,w)(c) = min over injective assignments of the negative columns sigma = 1..c to slots (j, r), j < l,
r < w, of sum max(0, sigma + j - r - 1): the Hall bound in the basis of beta-divided differences, where the
row Delta_j psi_q has pole order q - j.  E_(l,w)(c) is the plain assignment count (slots r, each l times).
The script tabulates E, E' and the conjectured exponent 2E for 2 <= l <= 5, 1 <= w <= 6, w <= c <= lw, and
reports where E' = 2E.  Exact minimum by dynamic programming over columns with per-slot usage (each slot
once).  Small integers; runs in well under a second.
"""
import sys
from functools import lru_cache


def plainE(l, w, c):
    rows = sorted(r for r in range(w) for _ in range(l))
    top = rows[len(rows) - c:]
    return sum(max(0, i + 1 - top[i] - 1) for i in range(c))


def ddE(l, w, c):
    # slots are characterized by capacity kappa = r - j + 1; cost of column sigma is max(0, sigma - kappa);
    # by the Monge property the optimum uses the c largest capacities in sorted order; checked by DP below.
    caps = sorted(r - j + 1 for j in range(l) for r in range(w))
    top = caps[len(caps) - c:]
    greedy = sum(max(0, i + 1 - top[i]) for i in range(c))
    kinds = sorted(set(caps))
    cnt = tuple(caps.count(k) for k in kinds)

    @lru_cache(maxsize=None)
    def dp(sigma, used):
        if sigma > c:
            return 0
        best = None
        for t, k in enumerate(kinds):
            if used[t] < cnt[t]:
                nu = list(used); nu[t] += 1
                v = max(0, sigma - k) + dp(sigma + 1, tuple(nu))
                best = v if best is None or v < best else best
        return best

    opt = dp(1, tuple(0 for _ in kinds))
    if opt != greedy:
        raise SystemExit(f"greedy {greedy} != optimum {opt} at l={l} w={w} c={c}")
    return opt


def main(out):
    lines = []
    for l in range(2, 6):
        for w in range(1, 7):
            row = []
            for c in range(w, l * w + 1):
                row.append((c, plainE(l, w, c), ddE(l, w, c), 2 * plainE(l, w, c)))
            sharp = [r[0] for r in row if r[2] == r[3]]
            lines.append(f"l={l} w={w}: (c, E, E', 2E) {row}; E' = 2E for c in {sharp}")
    txt = "\n".join(lines) + "\n"
    sys.stdout.write(txt)
    if out:
        with open(out, "w") as f:
            f.write(txt)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None)
