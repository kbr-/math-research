"""Part (2) of the window review's Decisive test: seven pigeons, six holes, D = 3, K = 2, partition-error pairs.

Reuses mixing_pairs_65.py's functions with its board parameters set to N = 6 holes (seven pigeons), D = 3, K = 2.
Errors E_A with |A| = 3; under the holes' symmetry a pair depends on |A cap B|, and the pigeon swap sends E_A to
E_{A^c}, keeping |A cap B|; overlap 0 means B = A^c, a congruent pair (E_A + E_B = Q_1 + Q_2 over F_2), so the two
non-congruent orbits are overlaps 1 and 2, both computed, with overlap 0 as a congruent control.
Statement tested: the window review's Prediction (c) and (d): dim J = a on every orbit, or b < dim J on some orbit,
or the outcome between them, a < b = dim J.
Expected: no outcome is predicted; dim J = I is expected on every orbit, since check:top-degree-partition-kernels
gives the single kernel at |A| = 3 as its representative sum (542) and the holes' symmetry carries it; asserted.
Refuted by: dim J different from I on some orbit, contradicting that sum carried by symmetry.
Possible because: a construction error at the new size would break the symmetry argument's premises.
Control: dim Ann_C(E_{0,1,2}) = 542, the recorded single kernel; asserted.
Refuted by: a different single kernel dimension.
Possible because: a different space convention at this size would change it.
Forced by counts: nothing forces 542; it is computed afresh.
Positive control: on the congruent orbit (overlap 0), dim J = 542, one error's kernel; asserted.
Refuted by: dim J different from 542 there.
Possible because: an intersection error would show there.
Baseline: a <= b <= I <= dim J; they decide nothing about the gaps.
Decisive at these sizes: exact dimensions, no seeds; a gap of one dimension between b and dim J decides.
Parallel use: fourteen worker processes over the first error's 128 representatives, one thread each.
Record checked: the claims read were check:top-degree-partition-kernels and conj:representative-sum-transfer,
with mixing_pairs_65.json; none gives a, b or I at this board.
"""
import argparse
import importlib.util
import json
import multiprocessing
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('mixing_pairs_65', HERE / 'mixing_pairs_65.py')
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)
mp.N, mp.D, mp.K = 6, 3, 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    st = mp.setup()
    single = len(mp.dl.ann_poly(st['cC'], st['monos'], mp.error((0, 1, 2))))
    assert single == 542, f'control: single kernel {single}'
    out = {'dim_V2': len(st['monos']), 'dim_W': len(st['W']), 'single_C_side': single, 'orbits': []}
    with multiprocessing.Pool(14) as pool:
        for overlap, B in ((0, (3, 4, 5)), (1, (0, 3, 4)), (2, (0, 1, 3))):
            r = mp.measure_orbit(pool, (3, 3, overlap), (0, 1, 2), B)
            if overlap == 0:
                assert r['J'] == 542, f'positive control {r}'
            out['orbits'].append(r)
            print(json.dumps(r), flush=True)
            pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
