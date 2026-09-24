import glob, json
tot = bad = 0
for p in sorted(glob.glob('research/results/bmd-r7-q-ary-scoping/q3/p*-n*-k*.json')):
    r = json.load(open(p)); q, n, k = r['p'], r['n'], r['k']
    for l, d in enumerate(r['delta']):
        m = k - l - 1
        phi = n * (q - 1) + q * l + (q - 1) * sum(m // q ** j for j in range(n))
        tot += 1; bad += d != phi
print(f'q-ary values {tot}; mismatches with n(q-1)+ql+(q-1)sum_(j<n) floor((k-l-1)/q^j): {bad}')
