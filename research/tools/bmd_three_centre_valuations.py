"""Cycle bmd-20261004-zx: characteristic-3 saturation valuation v3 = sum over steps of (D - rank) for each saved
three-centre run (N = 6..8), next to the characteristic-0 eps-order of the mark determinant from delta-q-7.txt."""
import re, glob
v3 = {}
for path in sorted(glob.glob('research/results/bmd-20261004-z[pqrtu]*/*.txt')):
    for line in open(path):
        m = re.search(r'sizes \[(\d+), (\d+), (\d+)\] N = (\d+), D = (\d+): saturation steps \d+, ranks \[([\d, ]+)\].*\((non)?classical\)', line)
        if m:
            D = int(m.group(5)); ranks = [int(x) for x in m.group(6).split(',')]
            ms = tuple(sorted(int(m.group(i)) for i in (1, 2, 3)))
            v3[ms] = (sum(D - r for r in ranks[:-1]), m.group(7) is None)
v0 = {}
for line in open('research/results/bmd-20261004-zx/delta-q-7.txt'):
    m = re.search(r'sizes \[(\d+), (\d+), (\d+)\].*char-0 eps-order (\d+)', line)
    if m:
        v0[tuple(sorted(int(m.group(i)) for i in (1, 2, 3)))] = int(m.group(4))
for ms in sorted(v0):
    print(ms, 'char-0 order', v0[ms], '; char-3 saturation valuation', v3.get(ms, ('?', '?'))[0], '; classical' if v3.get(ms, (0, False))[1] else '; nonclassical')
