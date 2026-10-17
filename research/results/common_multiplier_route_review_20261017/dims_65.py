"""The summed condition at six pigeons and five holes, D = 3, K = 2, for pairs of partition errors.

Same construction as mixing_pairs_65.py (its setup reused). Prints dim V_2 (the space its kernels live in), dim W =
C cap V_2, a single partition error's kernel dimension, its rank dim V_2 - dim Ann_C(E), the capacity
h = dim V_2 - dim W, and whether the summed condition fails for a pair (2 * rank >= h).
Statement tested: the reviewer's request that the summed condition at this board be stated.
Expected: dim W = 276 and dim Ann_C(E_{0,1}) = 332, the figures of mixing_pairs_65.json; asserted.
Refuted by: either figure different, which would mean a different construction from the run's.
Possible because: a changed setup would change them.
Control: the two figures above; asserted.
Forced by counts: nothing forces them; they are computed.
No positive control: the figures are dimensions, compared with a saved run.
Baseline: rank <= h always; it decides nothing about 2 * rank against h.
Record checked: the claims read were check:top-degree-partition-kernels and lem:exact-common-kernel-selection, which
give the single kernel and the criterion but not this board's dim V_2.
"""
import argparse
import importlib.util
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('mixing_pairs_65', HERE / 'mixing_pairs_65.py')
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    st = mp.setup()
    dimV, dimW = len(st['monos']), len(st['W'])
    single = len(mp.dl.ann_poly(st['cC'], st['monos'], mp.error((0, 1))))
    assert dimW == 276 and single == 332, (dimW, single)
    rank, h = dimV - single, dimV - dimW
    out = {'dim_V2': dimV, 'dim_W': dimW, 'single_kernel': single, 'single_rank': rank, 'capacity_h': h,
           'pair_summed_condition_fails': 2 * rank >= h,
           'pair_stacked_ranks': {str(J): dimV - J for J in (290, 300)}}
    print(json.dumps(out))
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
