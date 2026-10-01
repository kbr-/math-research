"""Cycle bmd-20261004-zw: does a simple symmetric invariant of the cluster sizes, taken mod 3 or mod 9 together with N,
separate classical from nonclassical three-centre multisets?  An invariant separates if no residue class (at fixed N)
contains both kinds.  Data from the saved outputs (N = 6..11)."""
import re, glob
from math import comb
cls = {}
for path in sorted(glob.glob('research/results/bmd-20261004-z[pqrtu]*/*.txt')):
    for line in open(path):
        m = re.search(r'sizes \[(\d+), (\d+), (\d+)\] N = \d+, D = (\d+).*\[(\d+), (\d+), (\d+)\] \((non)?classical\)', line)
        if m:
            cls[tuple(sorted(int(m.group(i)) for i in (1, 2, 3)))] = m.group(8) is None
inv = {
    'sum C(s,2)': lambda s: sum(comb(x, 2) for x in s),
    'e2 = sum s_a s_b': lambda s: s[0]*s[1] + s[0]*s[2] + s[1]*s[2],
    'e3 = product': lambda s: s[0]*s[1]*s[2],
    'sum s^3': lambda s: sum(x**3 for x in s),
    'sum C(s,3)': lambda s: sum(comb(x, 3) for x in s),
    'max': lambda s: max(s),
}
for name, f in inv.items():
    for q in (3, 9, 27):
        seen = {}
        clash = False
        for ms, c in cls.items():
            key = (sum(ms), f(ms) % q)
            if key in seen and seen[key] != c:
                clash = True
            seen[key] = c
        if not clash:
            print('SEPARATES:', name, 'mod', q)
print('scan done over', len(cls), 'multisets')
