"""Pencil graded Dade: check of the block table and of the case analysis (entry-2026-09-27-pencil-graded-dade).

Tested statements.
1. Block table (research/results/odd-prime-pencil-dade/blocks.jsonl, from pencil_freeness_blocks.m2): for a type
   r in {1,2,3}^4 with O = #{k : r_k = 2}, the first failure of P_r over T = F_3[A,B]/(A^3,B^3) is 1 + [O >= 2] when no
   r_k = 3; 1 + [O_j >= 1] + [O_j = 3] when exactly r_j = 3 (O_j counting the others); and P_r is free when two r_k = 3.
2. Case analysis: with n_k cells at the four points of P^1(F_3), e_k = floor(n_k/2) and eps_k = n_k mod 2, the minimum of
   sum_k e_k + f(1 + eps) and, over j with n_j >= 2, sum_{k != j} e_k + f(1 + eps with eps_j replaced by 2) equals
   floor((s + 3)/2), s = N - max_k n_k, except at n = (1,1,1,1), where it is 2.  Checked for all n in {0..BOUND}^4;
   the notebook entry proves it for all n by hand, and this check guards the arithmetic.
Usage: python3 pencil_dade_formula.py BLOCKS OUT
"""
import itertools
import json
import sys

BOUND = 12


def main():
    blocks, out = sys.argv[1], sys.argv[2]
    table = {}
    for line in open(blocks):
        row = json.loads(line)
        table[tuple(row["r"])] = row["first_failure"]
    assert len(table) == 81
    mismatches = []
    for r, f in table.items():
        threes = [k for k in range(4) if r[k] == 3]
        if len(threes) >= 2:
            want = -1
        elif not threes:
            odd = sum(x == 2 for x in r)
            want = 1 + (odd >= 2)
        else:
            odd = sum(r[k] == 2 for k in range(4) if k != threes[0])
            want = 1 + (odd >= 1) + (odd == 3)
        if f != want:
            mismatches.append({"r": list(r), "table": f, "pattern": want})
    exceptions = []
    count = 0
    for n in itertools.product(range(BOUND + 1), repeat=4):
        if sum(n) == 0:
            continue
        count += 1
        e = [x // 2 for x in n]
        base = tuple(1 + x % 2 for x in n)
        value = sum(e) + table[base]
        for j in range(4):
            if n[j] >= 2:
                r = list(base)
                r[j] = 3
                value = min(value, sum(e) - e[j] + table[tuple(r)])
        target = (sum(n) - max(n) + 3) // 2
        if value != target:
            exceptions.append({"n": list(n), "value": value, "target": target})
    result = {"table_pattern_mismatches": mismatches, "configurations": count, "bound": BOUND,
              "exceptions": exceptions}
    with open(out, "w") as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps({"mismatches": len(mismatches), "configurations": count, "exceptions": exceptions}))


if __name__ == "__main__":
    main()
