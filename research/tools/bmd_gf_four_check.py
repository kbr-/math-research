"""Check the four-element square conjecture against saved subspace-grid runs.

Conjecture: for a 4-element F_2-subspace S of GF(2^a) that is not a scaled subfield (the x^2
coefficient of L(x) = prod_{t in S}(x - t) is nonzero) and n = 2, the least degree with multiplicity
>= k at the nonzero points of S^2 and exactly l at the origin is 6 + 4(k-1) - h(m), m = k-l-1,
h(m) = 2 floor(m/8) + ceil((m mod 8)/2).  Also checks the base-s law of the scaled-subfield runs.
Usage: bmd_gf_four_check.py RESULTS a=poly ...
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from bmd_gf_summary import lcoeffs


def main():
    root = Path(sys.argv[1])
    polys = dict(tuple(map(int, x.split('='))) for x in sys.argv[2:])
    fit = bad = subfield_fit = subfield_bad = 0
    classes = set()
    for f in sorted(root.rglob('gf*-S*-n2-k*.json')):
        d = json.loads(f.read_text())
        a, S, k = d['a'], d['S'], d['k']
        if len(S) != 4:
            continue
        c = lcoeffs(a, polys[a], S)
        for l, v in enumerate(d['delta']):
            m = k - l - 1
            if c[1]:
                classes.add((a, tuple(S)))
                pred = 6 + 4 * (k - 1) - (2 * (m // 8) + (m % 8 + 1) // 2)
                fit += v == pred
                bad += v != pred
            else:
                pred = 6 + 4 * l + 3 * (m + m // 4)
                subfield_fit += v == pred
                subfield_bad += v != pred
    print(f'non-subfield 4-element subspaces: {len(classes)} {sorted(classes)}')
    print(f'four-element square conjecture: {fit} values fit, {bad} do not')
    print(f'scaled-subfield control (base-4 law): {subfield_fit} fit, {subfield_bad} do not')


if __name__ == '__main__':
    main()
