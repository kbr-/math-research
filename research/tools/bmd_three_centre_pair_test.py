"""Cycle bmd-20261004-zw: pairwise-product test of conj:cube-three-centre-leading-factorization.
Hypothesis: the mixed factor is a product of pair factors M(s_a, s_b), so a split is classical iff all three of its
cluster-size pairs are good.  Classical multisets force their pairs good; the hypothesis fails if some nonclassical
multiset has all three pairs forced good.  Data read from the saved three-centre outputs (N = 6..11)."""
import re, glob
cls = {}
for path in sorted(glob.glob('research/results/bmd-20261004-z[pqrtu]*/*.txt')):
    for line in open(path):
        m = re.search(r'sizes \[(\d+), (\d+), (\d+)\] N = \d+, D = (\d+).*\[(\d+), (\d+), (\d+)\] \((non)?classical\)', line)
        if m:
            ms = tuple(sorted(int(m.group(i)) for i in (1, 2, 3)))
            c = m.group(8) is None
            if ms in cls and cls[ms] != c:
                print('INCONSISTENT orderings for', ms)
            cls[ms] = c
print('multisets with a conclusive result:', len(cls), '; classical:', sum(cls.values()))
pairs = lambda ms: {tuple(sorted((ms[i], ms[j]))) for i in range(3) for j in range(i + 1, 3)}
good = set().union(*[pairs(ms) for ms, c in cls.items() if c])
bad_forced = [ms for ms, c in cls.items() if not c and pairs(ms) <= good]
print('pairs forced good:', sorted(good))
print('nonclassical multisets whose pairs are all forced good (contradictions):', bad_forced)
print('pairwise-product hypothesis', 'REFUTED' if bad_forced else 'consistent')
