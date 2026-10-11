#!/usr/bin/env python3
"""An explicit circuit of five three-spaces over F_2 spanning six dimensions, and the contraction counts.

Statement tested: with basis a, b, c, d, e, f of F_2^6, the three-spaces
  P1 = <a, b, c>, P2 = <a, b, d>, P3 = <a, c+d, e>, P4 = <a, b+e, f>, P5 = <a, b+e, c+d+f>
have trivectors summing to zero, no proper nonempty subset of them has trivectors summing to zero, and they
span six dimensions.  For every nonzero linear functional g on F_2^6 the number j(g) of members on which g is
not identically zero is never 1; it is 2 exactly when the two members share the plane on which g vanishes.

Expected before the run: sum zero, minimal, span 6; j(g) never 1 (a single contracted trivector is a nonzero
two-vector); j(g) = 2 does occur here, the example having members that meet in planes (P1 and P2 in <a, b>),
which is why it does not contradict the lemma for circuits without such pairs.  A failure of "sum zero" or
"minimal" would mean the example is wrong; a value j(g) = 1 would mean the contraction is implemented wrongly.
"""
import argparse
import itertools

N = 6
A, B, C, D, E, F = (1 << i for i in range(N))
MEMBERS = [(A, B, C), (A, B, D), (A, C ^ D, E), (A, B ^ E, F), (A, B ^ E, C ^ D ^ F)]
TRIPLES = list(itertools.combinations(range(N), 3))


def trivector(x, y, z):
    """The trivector x^y^z as a set of basis triples, over F_2."""
    out = set()
    for t in TRIPLES:
        det = 0
        for p in itertools.permutations(t):
            det ^= (x >> p[0] & 1) & (y >> p[1] & 1) & (z >> p[2] & 1)
        if det:
            out.add(t)
    return frozenset(out)


def rank(vectors):
    basis = []
    for v in vectors:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    tv = [trivector(*m) for m in MEMBERS]
    total = frozenset()
    for t in tv:
        total = total ^ t
    proper_zero = []
    for size in range(1, len(tv)):
        for sub in itertools.combinations(range(len(tv)), size):
            s = frozenset()
            for i in sub:
                s = s ^ tv[i]
            if not s:
                proper_zero.append(sub)
    span = rank([v for m in MEMBERS for v in m])
    counts = {}
    twos = []
    for g in range(1, 1 << N):
        live = [i for i, m in enumerate(MEMBERS) if any(bin(g & v).count("1") & 1 for v in m)]
        counts[len(live)] = counts.get(len(live), 0) + 1
        if len(live) == 2:
            twos.append(tuple(live))
    with open(args.out, "w") as fh:
        fh.write(f"sum_zero={not total} proper_subsets_summing_to_zero={proper_zero} span={span}\n")
        fh.write(f"functionals_by_number_of_live_members={dict(sorted(counts.items()))}\n")
        fh.write(f"pairs_live_alone={sorted(set(twos))}\n")
    assert not total and not proper_zero and span == 6 and 1 not in counts
    print("done")


if __name__ == "__main__":
    main()
