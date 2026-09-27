"""Exact single-top defect series from Jordan blocks (entry-2026-09-27-sharp-single-top).

Tested statement.  For tau = A^2 B on one row over F_3 with coefficient groups of sizes s1..s4 (A only, B only,
A+B type, A+2B type) and s0 unused cells, the Taylor defect in multiplier degree e is the coefficient of t^e in
    (1+t)^{s0} * sum over K subset {1..4} of prod_{k not in K} F_{s_k}(t) * t^{sum_{k in K} floor(s_k/2)} * D_{r(K)}(t),
where Lambda(s) = free + N_s (lem:pair-seed-decomposition: N_{2m} = J_1[m], N_{2m+1} = J_2[m]), F_s(t) =
((1+t)^s - N_s(t)) / (1+t+t^2) counts the free generators, r(K) has r_k = 3 off K and the parity type (1 even, 2 odd)
on K, and D_r is the block defect series of research/results/odd-prime-single-top/block_types.jsonl.  The program
computes, for every (s1..s4) in [0, SMAX]^4, the first degree with a nonzero defect and compares it with
the role-aware prediction min(floor(|A|/2), ceil(|B|/2), ceil(|A+B|/2), ceil(|A+2B|/2)), supports s1+s3+s4, s2+s3+s4,
s1+s2+s3, s1+s2+s4 (Wilson: a squared form fails at 2e+1 cells, an unsquared one at 2e).
It also prints the full series for a few size vectors, for comparison with direct rank computations.
Usage: python3 single_top_series.py BLOCKS OUT SMAX "s1:s2:s3:s4,..."
"""
import itertools
import json
import sys


def pmul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return out


def binom_series(s):
    out = [1]
    for _ in range(s):
        out = pmul(out, [1, 1])
    return out


def free_series(s):
    h = binom_series(s)
    m = s // 2
    n = [0] * (len(h))
    n[m] += 1
    if s % 2:
        n[m + 1] += 1
    num = [a - b for a, b in zip(h, n)]
    # divide by 1 + t + t^2 exactly
    q = [0] * max(1, len(num) - 2)
    r = num[:]
    for i in range(len(q)):
        c = r[i]
        q[i] = c
        for j, d in enumerate((1, 1, 1)):
            if i + j < len(r):
                r[i + j] -= c * d
    assert all(x == 0 for x in r), (s, r)
    assert all(x >= 0 for x in q), (s, q)
    return q


def defect_series(sizes, blocks, s0=0):
    total = [0]
    for K in itertools.chain.from_iterable(itertools.combinations(range(4), k) for k in range(5)):
        r = tuple(3 if k not in K else (1 if sizes[k] % 2 == 0 else 2) for k in range(4))
        # groups of size 0 or 1 have no free part
        if any(k not in K and sizes[k] <= 1 for k in range(4)):
            continue
        d = blocks.get(r)
        if not d or not any(d):
            continue
        ser = [0] * (sum(sizes[k] // 2 for k in K)) + d
        for k in range(4):
            if k not in K:
                ser = pmul(ser, free_series(sizes[k]))
        n = max(len(total), len(ser))
        total = [(total[i] if i < len(total) else 0) + (ser[i] if i < len(ser) else 0) for i in range(n)]
    return pmul(total, binom_series(s0))


def class_check(blocks):
    """Symbolic check for all sizes.  Write s_k = 2 a_k + p_k and b_k = [s_k >= 2] (b_k = 0 forces a_k = 0).  In a
    class (p, b) the first defect degree is min over contributing K of sum_{k in K} a_k + c_K, with c_K the order of
    D_{r(K)} (free groups need b_k = 1 and have a free generator in degree 0), and the prediction is min over the four
    combinations of sum_{k in supp} a_k + c'_T (floor or ceil of the parity sum over 2).  Substituting a_k = 1 + a'_k
    where b_k = 1 (a'_k >= 0), if every term of each side
    is bounded below, for all a >= 0, by a term of the other (support containment and constant comparison), the two
    agree for every size in the class.  Returns the classes where this fails."""
    supports = [(0, 2, 3), (1, 2, 3), (0, 1, 2), (0, 1, 3)]  # A, B, A+B, A+2B (groups 0-based)
    failures = []
    for p in itertools.product((0, 1), repeat=4):
        for b in itertools.product((0, 1), repeat=4):
            fterms = []
            for K in itertools.chain.from_iterable(itertools.combinations(range(4), k) for k in range(5)):
                if any(k not in K and not b[k] for k in range(4)):
                    continue
                r = tuple(3 if k not in K else (1 if p[k] == 0 else 2) for k in range(4))
                d = blocks[r]
                if not any(d):
                    continue
                # a_k = 1 + a'_k for groups with at least two cells, so each such group in K adds 1 to the constant
                fterms.append((frozenset(k for k in K if b[k]), next(i for i, x in enumerate(d) if x) + sum(b[k] for k in K)))
            gterms = []
            for j, T in enumerate(supports):
                ps = sum(p[k] for k in T)
                c = ps // 2 if j == 0 else (ps + 1) // 2
                gterms.append((frozenset(k for k in T if b[k]), c + sum(b[k] for k in T)))
            dom = lambda X, Y: all(any(Ky <= Kx and cy <= cx for Ky, cy in Y) for Kx, cx in X)
            if not (dom(fterms, gterms) and dom(gterms, fterms)):
                failures.append({"p": p, "b": b})
    return failures


def main():
    blocks = {}
    for line in open(sys.argv[1]):
        rec = json.loads(line)
        blocks[tuple(rec["r"])] = rec["defect_by_degree"]
    out = open(sys.argv[2], "w")
    smax = int(sys.argv[3])
    mismatches = []
    count = 0
    for sizes in itertools.product(range(smax + 1), repeat=4):
        ser = defect_series(sizes, blocks)
        first = next((i for i, x in enumerate(ser) if x), None)
        s1, s2, s3, s4 = sizes
        combos = [s1 + s3 + s4, s2 + s3 + s4, s1 + s2 + s3, s1 + s2 + s4]
        # squared form A: Wilson threshold 2e+2, first defect at floor(s/2); B + cA (unsquared modulo A):
        # threshold 2e+1, first defect at ceil(s/2)
        pred = min([combos[0] // 2] + [(c + 1) // 2 for c in combos[1:]])
        count += 1
        if first != pred:
            mismatches.append({"sizes": sizes, "first_defect": first, "predicted": pred, "earlier": first is not None and first < pred})
    fails = class_check(blocks)
    json.dump({"smax": smax, "size_vectors": count, "mismatches": len(mismatches), "examples": mismatches[:40],
               "class_check_failures": fails}, out)
    out.write("\n")
    for item in sys.argv[4].split(","):
        sizes = tuple(int(x) for x in item.split(":"))
        ser = defect_series(sizes, blocks)
        json.dump({"sizes": sizes, "series": ser}, out)
        out.write("\n")
    print("size vectors", count, "mismatches", len(mismatches))


if __name__ == "__main__":
    main()
