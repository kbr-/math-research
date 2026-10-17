"""Diagnostic, not committed: per restored level, the size of the restoring amplitudes and of the correction's
two coordinates against the dyadic field's spread, one seed at J = 6, shift 1, gain 1.

No statement tested: locates the variance growth seen in the smoke run.
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
lt, sr = rft.lt, rft.sr

J, N, seed, r0 = 6, 16 * 4 ** 6, 1, 1
rng = np.random.default_rng(seed)
cells = rng.multinomial(N, np.full(4 ** J, 4.0 ** -J)).reshape(1 << J, 1 << J)
G = 1 << (J + 1)
dy = np.zeros((2, G, G))
F = np.zeros((2, G, G))
st = {}
for j in range(J):
    sr.level_step(dy, cells, j, J, G, False, st)
    sr.level_step(F, cells, j, J, G, False, st)
    i = j - r0
    before = F.copy()
    rft.restore_step(F, i, G, 1.0)
    w = F - before
    print(f'step {j} restore level {i}: dyadic sd {dy[0].std():.1f} {dy[1].std():.1f}; correction sd '
          f'{w[0].std():.1f} {w[1].std():.1f}; restored sd {F[0].std():.1f} {F[1].std():.1f}; '
          f'max|w| {np.abs(w).max():.1f}')
m = 4
main, other = lt.unit_shapes(m)
print('unit shapes at m=4: main mean per child', main.mean(axis=(1, 2)), 'max|main|', np.abs(main).max(),
      'max|other|', np.abs(other).max())
