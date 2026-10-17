"""Diagnostic, not committed: the restored field's spread over the dyadic field's, per coordinate, against the
gain and J, shift 1 and 2, one seed; and the correction's spread at its last two levels, whose ratio is the growth.

No statement tested: chooses the gains for the run after the smoke run showed growth at gain 1.
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np

P = Path('/home/kbr/dev/math/.claude/worktrees/talagrand/research/results/ultimate_matching_restoring_flow_20261017')
sys.path.insert(0, str(P))
spec = importlib.util.spec_from_file_location('rft', P / 'restoring_flow_test.py')
rft = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rft)
for J in (6, 7, 8):
    N = 16 * 4 ** J
    for gain in (0.1, 0.25, 0.4, 0.5, 1.0):
        dy, rs = rft.fields(J, N, 1, gain=gain)
        row = [f'{rs[f][k].std() / dy[k].std():.3f}' for f in range(2) for k in range(2)]
        print(f'J={J} gain={gain}: sd ratio (r0=1: c1 c2; r0=2: c1 c2) ' + ' '.join(row), flush=True)
