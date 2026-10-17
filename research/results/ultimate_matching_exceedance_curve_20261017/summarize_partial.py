#!/usr/bin/env python3
"""Summarize the saved output of curve_test.py (partial_J5_J6.txt beside this script) against the Gaussian.

Usage: python3 summarize_partial.py --out gaussian_slopes.txt

For each finished size J and coordinate: each flow's exceedance fractions over the Gaussian ones, the slope in t
of log(rule / Gaussian) and of log(dyadic / Gaussian) beside the saved slope of log(rule / dyadic), and the
exceedance counts at the largest threshold. The number of positions per seed is the rule's own grid, G = 2^(J+1)
on each side (run() of research/results/ultimate_matching_simultaneous_rule_20261017/simultaneous_rule_test.py),
read from that script's source here rather than assumed, so G^2 = 4^(J+1) positions per seed; on 17 October 2026
a hand summary took 4^J and printed every count four times too small.

No statement tested: a summary of a saved run, which prints the quantities the entry reads and decides nothing.
"""
import argparse
import json
import math
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RULE = HERE.parent / 'ultimate_matching_simultaneous_rule_20261017' / 'simultaneous_rule_test.py'


def grid_shift():
    """The k in G = 1 << (J + k) of the rule's run(), read from its source."""
    found = re.search(r'G\s*=\s*1\s*<<\s*\(J\s*\+\s*(\d+)\)', RULE.read_text())
    if not found:
        raise SystemExit(f'{RULE}: no line G = 1 << (J + k) in run()')
    return int(found.group(1))


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--out', required=True)
    a = p.parse_args()
    shift = grid_shift()
    rows = [json.loads(line) for line in (HERE / 'partial_J5_J6.txt').read_text().splitlines()
            if line.startswith('{') and '"J"' in line]
    lines = [f'Grid: G = 2^(J + {shift}) positions per side, read from {RULE.name} run().']
    for r in rows:
        t, g = np.array(r['thresholds']), np.array(r['gaussian'])
        per_seed = (1 << (r['J'] + shift)) ** 2
        for c in ('coord1', 'coord2'):
            d, f, pl = (np.array(r[c][k]) for k in ('dyadic', 'rule', 'planted'))
            lines.append(f"J {r['J']} {c}: dyadic/Gaussian {np.round(d / g, 3).tolist()}; slope log(rule/Gaussian) "
                         f"{np.polyfit(t, np.log(f / g), 1)[0]:.3f}; slope log(dyadic/Gaussian) "
                         f"{np.polyfit(t, np.log(d / g), 1)[0]:.3f}; saved slope log(rule/dyadic) {r[c]['slope_rule']:.3f}")
            lines.append(f"   positions per seed {per_seed}, seeds {r['seeds']}; counts at t = {t[-1]}: dyadic "
                         f"{d[-1] * per_seed * r['seeds']:.1f}, rule {f[-1] * per_seed * r['seeds']:.1f}, planted "
                         f"{pl[-1] * per_seed * r['seeds']:.1f}")
    Path(a.out).write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
