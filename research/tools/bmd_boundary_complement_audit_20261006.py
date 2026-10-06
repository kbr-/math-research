#!/usr/bin/env python3
"""Stage the dated boundary certificate inventory for independent PARI verification.
Only JSON orchestration and small prime enumeration occur here; GP does algebra.
"""
import argparse
import hashlib
import json
from math import comb, isqrt
from pathlib import Path


def inventory():
    return [(n, p) for n in range(4, 9)
            for p in range((2**n if n <= 7 else 7) + 1,
                           max(n*(n+1)+1, 3*comb(n+1, 4)) + 1)
            if p > 2 and all(p % q for q in range(2, isqrt(p)+1))]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stage', choices=['control', 'sizing', 'all'], required=True)
    ap.add_argument('--out-gp', type=Path, required=True)
    ap.add_argument('--out-json', type=Path, required=True)
    args = ap.parse_args()
    root = Path('research/results/bmd-boundary-complement-20261006/certificates')
    pairs = {'control': [(4, 17)], 'sizing': [(8, 11)]}.get(args.stage, inventory())
    assert len(inventory()) == 99
    rows, entries = [], []
    for n, p in pairs:
        path = root / f'n{n}-p{p}.json'
        d = json.loads(path.read_text())
        e, N, m = d['field_degree'], n+1, comb(n+1, 2)+2
        weight, collision = N*comb(N, 2)+3*comb(N, 4), e*N*comb(N, 2)
        assert (d['status'], d['cube_dimension'], d['prime']) == ('certified', n, p)
        assert d['matrix_dimension'] == m and d['norm_matrix_dimension'] == e*m
        assert d['full_degree'] == weight and d['norm_degree'] == e*weight
        assert len(d['norm_determinant']) == e*weight+1 and d['norm_determinant'][-1] == 1
        assert len(d['gcd']) == collision+1 and d['gcd'][-1] == 1
        assert d['threshold'] == 3*comb(N, 4) and d['gcd_degree'] == collision
        assert len(d['modulus']) == e+1 and d['modulus'][-1] == 1
        assert len(d['intercept']) == len(d['direction']) == n
        assert all(len(a) == e for a in d['intercept']+d['direction'])
        assert len(d['additional_norm_minors']) == (m if d['all_cofactors'] else 0)
        rows.append([n, p, e, d['modulus'], d['intercept'], d['direction'],
                     d['norm_determinant'], d['norm_adjacent_minor'],
                     d['norm_vandermonde'], d['gcd'], d['additional_norm_minors']])
        entries.append({'n': n, 'p': p, 'e': e, 'path': str(path),
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'seconds': d['seconds'], 'line_attempt': d['line_attempt'],
                        'all_cofactors': d['all_cofactors']})
    report = {'stage': args.stage, 'count': len(rows), 'passed_shape_inventory': True,
              'algebra_check': 'Must also pass bmd_boundary_complement_verify_20261006.gp.',
              'counts_by_dimension': {str(n): sum(x['n'] == n for x in entries) for n in range(4, 9)},
              'certificates': entries}
    args.out_gp.parent.mkdir(parents=True, exist_ok=True)
    with args.out_gp.open('x') as f:
        f.write('FULL_CONTROL='+str(int(args.stage == 'control'))+';\n')
        f.write('DATA='+json.dumps(rows, separators=(',', ':'))+';\n')
    with args.out_json.open('x') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
    print(f'PASS {args.stage}: {len(rows)} certificate inventories; GP algebra verification still required.')


if __name__ == '__main__':
    main()
