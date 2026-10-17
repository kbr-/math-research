"""The even control the reviewer asked for: five pigeons, four holes, D = 2, K = 1, partition-error pairs, |A| = 2.

Reuses mixing_pairs_65.py's functions with N = 4 holes (five pigeons), D = 2, K = 1. check:top-degree-partition-
kernels records single excess 1 at |A| = 2 on this board (0, 0, 1, 0, 0 by |A|) and the sum over representatives
equal to the single kernel at the listed cases. Under the holes' symmetry a pair of 2-subsets depends on its
overlap; overlap 0 is the complement, a congruent pair; overlap 1 is the one non-congruent orbit.
Statement tested: whether the intersection kernel of four and six pigeons (n = 3, 5) appears at the even n = 4,
the parity hypothesis the window review names after its seven-pigeon board (n = 6) showed none.
Expected: no outcome is predicted; dim J = I is asserted by the shared measure function, from the single kernels'
representative sums carried by symmetry.
Refuted by: dim J different from I, which the shared assertion stops.
Possible because: the single-kernel sum equality is recorded for listed errors, and |A| = 2 here rests on it.
Control: on the congruent orbit, dim J equals the single kernel; asserted.
Refuted by: a different dim J there.
Possible because: an intersection error would show there.
Forced by counts: nothing forces the dimensions; they are computed.
No positive control: the four-pigeon board's run (mixing_pairs.json) is its positive control.
Baseline: a <= b <= I <= dim J; they decide nothing about the gaps.
Decisive at these sizes: exact dimensions, no seeds; one dimension between b and dim J decides.
Parallel use: fourteen worker processes over the first error's representatives, one thread each.
Record checked: the claims read were check:top-degree-partition-kernels and conj:representative-sum-transfer,
with mixing_pairs.json and mixing_pairs_76.json; none gives a, b or I at this board.
"""
import argparse
import importlib.util
import json
import multiprocessing
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('mixing_pairs_65', HERE / 'mixing_pairs_65.py')
mp = importlib.util.module_from_spec(spec)
sys.modules['mixing_pairs_65'] = mp     # so the pool's worker function pickles (see mixing_pairs_76.py)
spec.loader.exec_module(mp)
mp.N, mp.D, mp.K = 4, 2, 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    st = mp.setup()
    single = len(mp.dl.ann_poly(st['cC'], st['monos'], mp.error((0, 1))))
    out = {'dim_V1': len(st['monos']), 'dim_W': len(st['W']), 'single_C_side': single, 'orbits': []}
    with multiprocessing.Pool(14) as pool:
        for overlap, B in ((0, (2, 3)), (1, (0, 2))):
            r = mp.measure_orbit(pool, (2, 2, overlap), (0, 1), B)
            if overlap == 0:
                assert r['J'] == single, f'control {r}'
            out['orbits'].append(r)
            print(json.dumps(r), flush=True)
            pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
