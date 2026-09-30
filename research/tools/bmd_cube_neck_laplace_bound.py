"""Combinatorial Laplace bound for the neck windows (1 October 2026; cycle bmd-20261001-c).

Rows (j, p), 0 <= j < l, 0 <= p < w.  For a set R of c rows (those placed on the negative columns),
    Phi(R) = c(c+1)/2 + bump(R) + sum_{(j,p) not in R} p + sum_j m_j (m_j + 1) / 2,
where bump(R) is the sum of the bumped sorted orders p + j over R (b_k = max(o_(k), b_(k-1) + 1)) and m_j is the
number of rows of species j outside R.  Tested statement: min_R Phi(R) = l w^2 + 2 E_(l,w)(c) for w <= c <= l w,
with E the assignment count, 2E = d(d+1) + 2ad - (l-1)a(a+1), d = c - w = (l-1)a + b (lem:cube-neck-assignment-
identity).  Exhaustive over subsets for small sizes; prints every mismatch.
"""
import argparse
import itertools


def two_e(l, w, c):
    d = c - w
    a, b = divmod(d, l - 1)
    return d * (d + 1) + 2 * a * d - (l - 1) * a * (a + 1)


def phi(l, w, c, R):
    orders = sorted(p + j for (j, p) in R)
    bump, prev = 0, -1
    for o in orders:
        prev = max(o, prev + 1)
        bump += prev
    Rs = set(R)
    rest = [(j, p) for j in range(l) for p in range(w) if (j, p) not in Rs]
    m = [0] * l
    for j, _ in rest:
        m[j] += 1
    return c * (c + 1) // 2 + bump + sum(p for _, p in rest) + sum(x * (x + 1) // 2 for x in m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--maxrows", type=int, default=18)
    args = ap.parse_args()
    lines, bad = [], 0
    for l in range(2, 7):
        for w in range(1, 9):
            if l * w > args.maxrows:
                continue
            rows = [(j, p) for j in range(l) for p in range(w)]
            for c in range(w, l * w + 1):
                best, arg = None, None
                for R in itertools.combinations(rows, c):
                    v = phi(l, w, c, R)
                    if best is None or v < best:
                        best, arg = v, R
                target = l * w * w + two_e(l, w, c)
                ok = best == target
                bad += not ok
                lines.append(f"l={l} w={w} c={c}: min Phi = {best}, l w^2 + 2E = {target}, {'ok' if ok else 'MISMATCH'}; "
                             f"a minimizer R = {list(arg)}")
    lines.append(f"windows checked: {len(lines)}; mismatches: {bad}")
    with open(args.out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(lines[-1])


if __name__ == "__main__":
    main()
