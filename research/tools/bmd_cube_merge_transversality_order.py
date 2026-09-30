#!/usr/bin/env python3
"""Lowest T-order of the merge window determinant at beta_j = T^(j-1) (cycle bmd-20261001-y).

Predicts the order from the greedy block structure of the transversality proof and compares it
with the exact orders in research/results/bmd-20261001-x/transversality-hier.txt.
"""
import re
# predicted lowest T-order of det X at beta_j = T^(j-1) from the greedy block structure
def pred(n, K, a):
    si = n * (n - 1) // 2 - 1          # sum of row indices -1..n-1 in a block
    cost, nxt_main = 0, n              # block K: main -1..n-1
    for p in range(1, K):              # block j = K - p, weight j - 1 = K - p - 1
        w = K - p - 1
        if p < a:
            cols = [p - 1] + list(range(nxt_main, nxt_main + n)); nxt_main += n
        else:
            cols = list(range(nxt_main, nxt_main + n + 1)); nxt_main += n + 1
        cost += w * (sum(cols) - si)
    assert nxt_main == (n + 1) * K - a, (n, K, a)
    return cost
ok = True
for line in open('research/results/bmd-20261001-x/transversality-hier.txt'):
    m = re.match(r'n=(\d+) K=(\d+) a=(\d+): .*lowest order=(\d+)', line)
    n, K, a, low = map(int, m.groups())
    if pred(n, K, a) != low:
        ok = False; print('mismatch', n, K, a, pred(n, K, a), low)
print('all match' if ok else 'MISMATCH')
