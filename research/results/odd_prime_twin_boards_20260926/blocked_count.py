#!/usr/bin/env python3
"""Count blocked centres on the boards of twin_filling.py (same seed and generation order).

A pigeon r is a blocked centre if its holes h_1..h_d (all of them) can be matched to distinct
other pigeons n_1..n_d with n_i adjacent to h_i, such that every n_i has a hole adjacent to no
other row of S = {r, n_1..n_d} (prop:blocked-centre-unfilled). Exhaustive search over the leg
assignments of each pigeon. Also reports duplicate rows (twin pigeons).
Usage: blocked_count.py --out PATH [--P 121] [--Q 60] [--d 2] [--seed 20260926]
"""
import argparse, itertools, json, sys
import numpy as np
sys.path.insert(0, '/home/kbr/dev/math-auxiliary/research/results/odd_prime_twin_boards_20260926')
from twin_filling import twin_board, random_board


def is_blocked(nbrs, r, hole_rows):
    holes = sorted(nbrs[r])
    cands = [[p for p in hole_rows[h] if p != r] for h in holes]
    for legs in itertools.product(*cands):
        if len(set(legs)) < len(legs):
            continue
        S = (r,) + legs
        ok = True
        for n in legs:
            others = set().union(*(nbrs[q] for q in S if q != n))
            if not (nbrs[n] - others):
                ok = False
                break
        if ok:
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--P', type=int, default=121)
    ap.add_argument('--Q', type=int, default=60)
    ap.add_argument('--d', type=int, default=2)
    ap.add_argument('--seed', type=int, default=20260926)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    boards = {'twin': twin_board(rng, a.P, a.Q, a.d),
              'random_control': random_board(rng, a.P, 2 * a.Q, 2 * a.d)}
    res = {'params': vars(a), 'boards': {}}
    for name, nbrs in boards.items():
        hole_rows = {}
        for i, N in enumerate(nbrs):
            for h in N:
                hole_rows.setdefault(h, []).append(i)
        blocked = sum(is_blocked(nbrs, r, hole_rows) for r in range(len(nbrs)))
        dup = len(nbrs) - len(set(nbrs))
        res['boards'][name] = {'pigeons': len(nbrs), 'blocked_centres': blocked, 'duplicate_rows': dup}
        print(name, res['boards'][name], flush=True)
    json.dump(res, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
