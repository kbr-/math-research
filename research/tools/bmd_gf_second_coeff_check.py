"""Check the second-coefficient lemma against saved subspace-grid runs.

Lemma: if S is an F_2-subspace of GF(2^a) with |S| = s >= 4 and the x^2 coefficient c_1 of
L(x) = prod_{t in S}(x - t) is nonzero, then for n >= 2 and k >= 3 the least degree with multiplicity
>= k at the nonzero points of S^n and exactly l = k-3 at the origin is n(s-1) + s(k-1) - 1
(savings h = 1 at m = k-l-1 = 2), one more than the base-s law.  Also reports the saved runs with
c_1 = 0 at m = 2 for contrast.
Usage: bmd_gf_second_coeff_check.py RESULTS a=poly ...
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from bmd_gf_summary import lcoeffs


def main():
    root = Path(sys.argv[1])
    polys = dict(tuple(map(int, x.split('='))) for x in sys.argv[2:])
    fit, bad, other = 0, [], {}
    for f in sorted(root.rglob('gf*-S*-n*-k*.json')):
        d = json.loads(f.read_text())
        a, S, n, k = d['a'], d['S'], d['n'], d['k']
        s = len(S)
        if n < 2 or k < 3 or s < 4:
            continue
        v = d['delta'][k - 3]
        h = n * (s - 1) + s * (k - 1) - v
        c = lcoeffs(a, polys[a], S)
        if c[1]:
            if h == 1:
                fit += 1
            else:
                bad.append((a, S, n, k, h))
        else:
            other.setdefault((a, tuple(S), n), set()).add(h)
    print(f'c_1 != 0, n >= 2, k >= 3, l = k-3: {fit} values have h = 1; exceptions: {bad}')
    for key, hs in sorted(other.items()):
        print(f'c_1 = 0: GF(2^{key[0]}) S={list(key[1])} n={key[2]}: h at m = 2 is {sorted(hs)}')


if __name__ == '__main__':
    main()
