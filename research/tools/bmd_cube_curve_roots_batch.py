import re
log = open('research/results/bmd-20260930-zzh/n6-control.txt').read()
blocks = log.split('== ')[1:]
out = ['# At each linear factor of gcd(A, B) from n6-control: triple roots of R, involution pairings (N = 6).']
b = '2 3/7 -5/3 11/4 -1 7/2'
for blk, mask in zip(blocks, ['100000', '111000']):
    fac = re.search(r'gcd factors \(degree\^multiplicity\): (.*)', blk).group(1).split()
    roots = re.findall(r'root s = (\d+)', blk)
    lin = [f for f in fac if f.startswith('1^')]
    assert len(lin) == len(roots), (len(lin), len(roots))
    for f, r in zip(lin, roots):
        out.append(f'# factor {f} on mask {mask}')
        out.append(f'at 6 190 115 {mask} {r} {b}')
open('research/results/bmd-20260930-zzh/n6-roots.batch', 'w').write('\n'.join(out) + '\n')
print(len(out))
