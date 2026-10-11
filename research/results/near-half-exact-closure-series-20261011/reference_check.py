"""Cross-check of the closure kernel's degree three against the Python reference on parity 2-clause instances.

The reference tools/truncated_buchberger.py computes the polynomial-calculus degree independently; it is run
here through degree 3 on instances where the kernel gives degree 3.  (This file was first written against a
wrong run, in which a faulty product made every instance have degree 3; with the product corrected the kernel
gives 3 at n = 12, 16 and 4 from n = 20.)

Usage: python3 reference_check.py OUT.json
"""
import importlib.util
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'tools'))
import truncated_buchberger as tb

spec = importlib.util.spec_from_file_location('closure_series', HERE / 'closure_series.py')
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)


def check(n, seed):
    rows = cs.instance(n, seed)
    reference = [{tuple(1 if m >> i & 1 else 0 for i in range(n)) for m in p} for p in rows]
    start = time.time()
    return {'n': n, 'seed': seed, 'reference_degree_through_3': tb.pc_degree(reference, n, 3),
            'seconds': round(time.time() - start, 1)}


def main(out):
    results = []
    # n = 20 through degree 3 did not finish in a minute in the reference and is not run; so the reference
    # confirms the kernel's refutations at degree 3 and not its absence of one at n = 20
    for n, seed in ((12, 1), (16, 1), (16, 2)):
        results.append(check(n, seed))
        with open(out, 'w') as handle:
            json.dump(results, handle, indent=1)
        print(json.dumps(results[-1]), flush=True)


if __name__ == '__main__':
    main(sys.argv[1])
