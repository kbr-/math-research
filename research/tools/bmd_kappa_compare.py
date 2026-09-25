"""Compare exact per-order savings on S^2 with the root-curve orders kappa(m).

Statement tested (stable per-order law).  For every F_2-subspace S and m = k-l-1, the savings
h(k, l) = n(s-1) + s(k-1) - delta_S(n,k,l) satisfy h <= kappa(m) = min{d : m in Ord(d)} for all l,
with equality once l is large.  Reads the kernel outputs (bmd_gf_series.py JSON files) and a KAPPA
line printed by bmd_root_curve_orders_n.py (subspace mode; the first trial with no COUNT DIFFER) and reports, for each m with a known
kappa: the savings by l, whether all are <= kappa(m), and whether the largest l attains kappa(m).
Usage: bmd_kappa_compare.py KERNEL_DIR KAPPA_FILE n
"""
import json, sys
from pathlib import Path


def main():
    kdir, kfile, n = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
    lines = kfile.read_text().splitlines()
    # use the first trial whose counts all match N_{s,n}(d) (a generic specialization)
    bad = {l.split(' trial ')[1].split()[0] for l in lines if 'COUNT DIFFER' in l}
    line = next(l for l in lines if l.startswith('KAPPA') and l.split()[2].rstrip(':') not in bad)
    kappa = {int(a): int(b) for a, b in (x.split(':') for x in line.split(': ', 1)[1].split())}
    dmax = max(kappa.values())
    sav = {}
    for f in kdir.glob('gf*-n%d-k*.json' % n):
        d = json.loads(f.read_text())
        s, k = len(d['S']), d['k']
        for l, v in enumerate(d['delta']):
            sav.setdefault(k - l - 1, {})[l] = n * (s - 1) + s * (k - 1) - v
    bad_upper, bad_stable = [], []
    for m in sorted(sav):
        row = sav[m]
        top = row[max(row)]
        if m in kappa:
            if max(row.values()) > kappa[m]:
                bad_upper.append(m)
            if top != kappa[m]:
                bad_stable.append(m)
            status = f'kappa={kappa[m]}'
        else:
            status = f'kappa>{dmax}'
            if max(row.values()) <= dmax and top <= dmax:
                pass
        print(f'm={m} {status} savings by l: ' + ' '.join(str(row[l]) for l in sorted(row)), flush=True)
    print(f'savings above kappa: {bad_upper}; largest l below kappa: {bad_stable}')


if __name__ == '__main__':
    main()
