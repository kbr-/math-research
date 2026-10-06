#!/usr/bin/env python3
"""Audit the two retained N=8 line-certificate runs; never recompute a determinant.

This bounded one-off research evidence check compares their numerical kernels with
an already reviewed driver and verifies exactly the requested prime inventory.
It does not infer a uniform coprimality theorem from finite certificates.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    reference = Path('research/tools/bmd_boundary_coprimality_lines.gp')
    drivers = [Path('research/tools/bmd_review_boundary_n8.gp'),
               Path('research/tools/bmd_review_boundary_n8_large.gp')]
    logs = [Path('research/results/bmd-20261009-kcd/boundary-n8.txt'),
            Path('research/results/bmd-20261009-kck/boundary-n8-large.txt')]
    def kernel(path):
        match = re.search(r'lineminors\(N, p, e\) = \{.*?\n\}', path.read_text(), re.S)
        assert match, path
        return re.sub(r'\s+', '', match[0])
    expected_kernel = kernel(reference)
    rows = []
    groups = []
    for driver, log in zip(drivers, logs):
        source = driver.read_text()
        assert kernel(driver) == expected_kernel, driver
        assert 'poldegree(D) == full' in source
        assert 'poldegree(gcd(D, Dp)) == N * poldegree(V)' in source
        text = log.read_text()
        assert '# command: gp -q ' + str(driver) in text
        assert 'not a function' not in text and 'Error' not in text
        parsed = re.findall(r'^N=(\d+) p=(\d+) certified: (\d+) deg Delta (\d+) '
                            r'\(full (\d+)\) time (\d+) s$', text, re.M)
        assert parsed, log
        primes = []
        for raw in parsed:
            n, p, ok, degree, full, seconds = map(int, raw)
            assert (n, ok, degree, full) == (8, 1, 434, 434), raw
            primes.append(p)
            rows.append(p)
        groups.append({'path': str(log), 'count': len(primes), 'primes': primes})
    expected = [p for p in range(3, 128, 2)
                if all(p % q for q in range(2, int(p**0.5) + 1))]
    assert sorted(rows) == expected and len(set(rows)) == len(rows)
    evidence = [reference] + drivers + logs
    report = {'passed': True, 'scope': 'Existing finite N=8 certificate coverage only; no new determinant run.',
              'N': 8, 'cube_dimension': 7, 'boundary_order': 30, 'threshold': 210,
              'full_degree': 434, 'count': len(rows), 'expected_odd_primes_through': 127,
              'groups': groups, 'kernel_matches_reviewed_driver': True,
              'files': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                        for p in evidence]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
    print('PASS: 5 + 25 = 30 distinct odd-prime certificates, exactly 3 through 127.')
    print('Both kernels match the reviewed driver; all full-degree and gcd-degree checks passed.')
    print('Existing result: dimension7 boundary order30 has threshold210 at these primes.')


if __name__ == '__main__':
    main()
