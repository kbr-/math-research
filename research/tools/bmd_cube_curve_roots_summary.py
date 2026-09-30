import re, collections
t = open('research/results/bmd-20260930-zzh/n6-roots.txt').read()
spec = open('research/results/bmd-20260930-zzh/n6-roots.batch').read().split('\n')
facs = [l[len('# factor '):] for l in spec if l.startswith('# factor')]
blocks = t.split('== ')[1:]
assert len(blocks) == len(facs)
c = collections.Counter()
for f, b in zip(facs, blocks):
    mult = f.split()[0]; mask = f.split()[-1]
    if 'check points FAIL' in b: kind = 'collision (branch points meet)'
    else:
        dq = int(re.search(r'degQ (-?\d+)', b).group(1)); g3 = int(re.search(r"gcd\(R,R',R''\) (-?\d+)", b).group(1))
        inv = 'involution' if 'involution pairing' in b and 'no involution' not in b else 'no involution'
        kind = f'degQ {dq}, deg gcd(R,R\',R\'\') {g3}, {inv}'
    c[(mask, mult, kind)] += 1
for k, v in sorted(c.items()): print(v, k)
