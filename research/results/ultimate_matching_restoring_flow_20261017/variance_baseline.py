#!/usr/bin/env python3
"""The baseline the analytic-normalization ratios of results.json must be read beside: if the restored field were
the dyadic field's Gaussian law scaled by s = sqrt(variance ratio) (the run's own spatially averaged ratio), its
exceedance fraction at t analytic standard deviations would be P(|Z| > t/s), so the ratio to the dyadic flow's
would be erfc(t/(s sqrt 2)) / erfc(t/sqrt 2). Printed beside the observed ratio and its bootstrap spread, per
level, configuration and coordinate.

No statement tested: a baseline for reading results.json (COMPUTATION_RULES.md: a ratio is read beside each
part's own baseline). The scaling is spatially averaged, an approximation where the variance ratio varies with
position, so a gap of a few spreads is not by itself a shape effect.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    d = json.loads((HERE / 'results.json').read_text())
    T = d['T_ANA']
    for e in d['results']:
        for f, (cfg, s) in enumerate(e['shifts'].items()):
            for k in range(2):
                sc = math.sqrt(e['variance_ratio'][f][k])
                base = [math.erfc(t / (sc * math.sqrt(2))) / math.erfc(t / math.sqrt(2)) for t in T]
                obs = s['ana_ratio'][k]
                row = ' '.join(f't={t}: obs {o[0]:.2f}+-{o[1]:.2f} base {b:.2f}' for t, o, b in zip(T, obs, base))
                print(f"J={e['J']} cfg={cfg} coord={k + 1} s={sc:.3f}: {row}")


if __name__ == '__main__':
    main()
