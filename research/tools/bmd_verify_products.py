"""Verify P = prod(1+x_i) * Q_k in concrete dimensions with the C++ direct Hasse evaluation.

For each k and n in the grid, expands P and runs `bmd_min_degree verify n k FILE`, recording the
degree (expected n + 2k - m(k)), origin order and least nonzero multiplicity.  Orchestration only.
Usage: bmd_verify_products.py BINARY QJSON OUTJSON
"""
import json, math, subprocess, sys, tempfile, os
here = os.path.dirname(os.path.abspath(__file__))
binary, qjson, outjson = sys.argv[1:4]
results = []
for rec in json.load(open(qjson)):
    k = rec['k']
    for n in sorted({3, 4, 5, 6, 7, k - 1, k, k + 1} - {0, 1, 2}):
        if n > 7:
            continue                    # 2^n points x expanded monomials; keep each check to seconds
        with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
            path = f.name
        subprocess.run([sys.executable, os.path.join(here, 'bmd_expand_product.py'), qjson, str(k), str(n), path],
                       check=True, capture_output=True)
        r = subprocess.run([binary, 'verify', str(n), str(k), path], capture_output=True, text=True)
        os.unlink(path)
        line = r.stdout.strip()
        expected = n + 2 * k - (int(math.log2(k)) + 2)
        deg = int(line.split('degree=')[1].split()[0])
        ok = line.endswith('OK') and deg == expected
        results.append({'k': k, 'n': n, 'line': line, 'expected_degree': expected, 'ok': ok})
        print(('PASS ' if ok else 'FAIL ') + line, flush=True)
json.dump(results, open(outjson, 'w'), indent=1)
print('all passed' if all(r['ok'] for r in results) else 'FAILURES PRESENT')
