"""Refutation degrees of the product-axiom pigeonhole systems, to see whether any proper closure lies
above the pigeon axioms' degree n.

Statement tested: for m = n+1 pigeons and n = 2, 3, 4 holes (pigeon axioms prod_j (1+x_ij), hole axioms,
F_2, multilinear), the PC refutation degree is n+1, so no closure of degree above n is proper and every
proper window lies in the range where the pigeon axioms are inert.
Expected: degrees 3, 4, 5 (the first two are recorded by earlier checks).
Refuted by: a refutation degree above n+1 for some n, giving a proper closure above degree n.
Possible because: PC degree lower bounds for pigeonhole grow with n, so degree n+1 could fail to
refute at n = 4.
"""
import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import pc_closure as pc


def php(m, n):
    v = lambda i, j: i * n + j
    axioms = []
    for i in range(m):
        p = {0}
        for j in range(n):
            p = pc.multiply(p, {0, 1 << v(i, j)})
        axioms.append(sorted(p))
    for j in range(n):
        for i in range(m):
            for k in range(i + 1, m):
                axioms.append([(1 << v(i, j)) | (1 << v(k, j))])
    return axioms, m * n


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        binary = str(pathlib.Path(tmp) / 'fcd')
        subprocess.run(['g++', '-O2', '-o', binary, str(ROOT / 'tools' / 'f2_closure_degree.cpp')], check=True)
        for n in (2, 3, 4):
            axioms, nv = php(n + 1, n)
            path = pathlib.Path(tmp) / 'instance.txt'
            path.write_text(f'{nv} {len(axioms)}\n' + ''.join(f'{len(p)} ' + ' '.join(map(str, p)) + '\n'
                                                            for p in axioms))
            out = json.loads(subprocess.run([binary, str(path), str(n + 1)], check=True, capture_output=True,
                                            text=True).stdout)
            rows.append(dict(holes=n, pigeons=n + 1, result=out))
            print(json.dumps(rows[-1]), flush=True)
    pathlib.Path(args.out).write_text(json.dumps(rows, indent=1) + '\n')
    assert [r['result']['degree'] for r in rows] == [3, 4, 5], [r['result']['degree'] for r in rows]
    print('PASS')


if __name__ == '__main__':
    main()
