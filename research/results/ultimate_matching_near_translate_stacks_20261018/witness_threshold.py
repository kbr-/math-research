"""No statement tested: the size of N from which thm:offset-tree-stacks (c)'s condition ln(n+1) <= (log(v/2))^(1/4)
holds on the near translate stacks entry's Nonvacuity witness, with n about (1/2) log_2 N and v = e^((log N)^(1/2)),
so log(v/2) about (log N)^(1/2): the two sides printed at log N = 10^11 and 10^12 (18 October 2026)."""
import math

for logN in (1e11, 1e12):
    n = 0.5 * logN / math.log(2)
    left = math.log(n + 1)
    right = (math.sqrt(logN) - math.log(2)) ** 0.25
    print(f'log N = {logN:.0e}: n + 1 = {n + 1:.2e}, ln(n+1) = {left:.1f}, (log(v/2))^(1/4) = {right:.1f}, '
          f'holds: {left <= right}')
