"""Which pre-stable pairs (d, rho), rho >= 2, decide a recorded value: d is the last d with B(d, rho) <= l, or the
first d with B(d, rho) > l, among 5d > m+1, d <= floor(m/4)."""
import glob, json, sys
sys.path.insert(0, 'research/tools')
from bmd_cube_formula_check import B
out = {}
for path in glob.glob('research/results/**/*.json', recursive=True):
    try:
        data = json.load(open(path))
    except (ValueError, UnicodeDecodeError):
        continue
    if not isinstance(data, dict) or data.get('grid') != 2 or data.get('n') != 3:
        continue
    p, k = data['p'], data['k']
    for l in range(k):
        m = k - l - 1
        if m == 0:
            continue
        for d in range(1, m // 4 + 1):
            rho = m + 1 - 4 * d
            if 5 * d > m + 1 and rho >= 2 and B(d, rho) in (l, l + 1):
                out.setdefault(p, set()).add((d, rho))
for p in sorted(out):
    print(f"p={p}: {len(out[p])} pre-stable pairs with rho >= 2 at their threshold: {sorted(out[p])}")
