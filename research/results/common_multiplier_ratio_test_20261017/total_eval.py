"""Whether evaluation at the total matchings embeds A_K = V_K(B)/W_K(B) on satisfiable reduced boards, over F_2.

Statement tested (the reviewer's suggestion for the closure model on boards with at most as many pigeons as holes):
the evaluation of V_K(B) at the total matchings (each pigeon in its own hole) has kernel exactly W_K(B) modulo H,
that is rank dim A_K, so that the general single-functional lemma applies modulo the closure there.
The extreme the question needs: W_K vanishes at every total matching (each Q_i is 0 there), so the rank is at most
dim A_K; the test is whether it equals dim A_K.
Expected: rank equal to dim A_K at K = 2 on the 3- and 4-pigeon boards with 8 holes (dim A_2 = 145 and 275).
Refuted by: a rank below dim A_K on some board run, a low-degree function vanishing on all total matchings
outside W_K.
Possible because: the degree-K part of the vanishing ideal of the total matchings may exceed the span of the
pigeon-axiom multiples of degree K.
Control: the rank never exceeds dim A_K, asserted, since W_K vanishes on the total matchings.
Refuted by: a rank above dim A_K, which would mean W_K or the evaluation is built wrongly.
Possible because: a sign or row error in the generators would break their vanishing.
No positive control: no board is known here where the rank falls short; the control above is the one that can fail.
Baseline: the count of total matchings (336 and 1680) bounds the rank from above and decides nothing about it.
Record checked: lem:native-restriction (A_k), check:native-ratio-counts (the dimensions 145, 275); none gives
this rank.
"""
import argparse
import importlib.util
import itertools
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from f2_span import Span

spec = importlib.util.spec_from_file_location('nkl', pathlib.Path(__file__).with_name('native_kl.py'))
nkl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nkl)


def run(m, n, K):
    b = nkl.Board(m, n, K)
    W = Span(b.W(K))
    dimA = len(b.upto[K]) - len(W)
    points = [sum(b.bit[(i, h)] for i, h in enumerate(hs)) for hs in itertools.permutations(range(n), m)]
    rows = Span()
    for mm in b.upto[K]:
        vec = 0
        for j, pt in enumerate(points):
            if mm & pt == mm:
                vec |= 1 << j
        rows.add(vec)
    rank = len(rows)
    assert rank <= dimA, 'rank above dim A_K: W_K does not vanish on total matchings'
    return {'pigeons': m, 'holes': n, 'K': K, 'dim_VK': len(b.upto[K]), 'dim_AK': dimA, 'total_matchings': len(points),
            'rank': rank, 'embeds': rank == dimA}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    res = [run(m, 8, 2) for m in (3, 4)]
    pathlib.Path(args.out).write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps(res))


if __name__ == '__main__':
    main()
