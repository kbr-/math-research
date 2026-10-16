"""A prediction at a new size: the top-degree excess of the balanced partition error at seven by six.

System: functional pigeonhole over F_2, 7 pigeons, 6 holes, multilinear, D = 3 = ceil(6/2) (the top), K = 2,
computed by the route of independent_top.py (no tools/pc_closure.py), which agreed with top_search.json at
4x3, 5x4 and 6x5. Errors E_A = sum_{j<a} x1j + sum_{j>=a} x2j for a = 3 (balanced) and a = 0.
Statement tested: the untested hypothesis drawn from n = 3, 4, 5 (top_search.json): at D = ceil(n/2), K = D - 1,
the balanced partition error has positive excess and the one-pigeon error E_0 has excess 0.
Expected: excess(a=3) > 0 and excess(a=0) = 0.
Refuted by: excess 0 at a = 3, or a positive excess at a = 0.
Possible because: three sizes, two of them at D = 2, are thin evidence; even n gave excess at one |A| only.
Control: E_0 = sum_j x2j = 1 + Q_2 has the kernel of the constant 1, which has no extra killer; excess 0.
Refuted by: a positive excess at a = 0.
Possible because: a bug at this size in the route would show spurious killers.
Positive control: the same route found excess 12 at 6x5 (independent_top.json); asserted there, not rerun here.
Baseline: the bare count bounds the excess by dim V_2 = 904 minus the domain part; it decides nothing.
Decisive at these sizes: one positive excess or one zero at a = 3 decides the prediction; exact, no seeds.
Parallel use: fourteen worker processes over chunks of the 128 representatives, one thread each.
Record checked: the claims read were conj:linear-kernel-transfer, lem:closure-degree-locality and
check:functional-kernels-k2 (variables at K=2 at 7x6, excess 0); none decides partition errors here.
"""
import argparse
import importlib.util
import itertools
import json
import multiprocessing
import pathlib

spec = importlib.util.spec_from_file_location('independent_top',
                                              pathlib.Path(__file__).with_name('independent_top.py'))
it = importlib.util.module_from_spec(spec)
spec.loader.exec_module(it)

N, D, K = 6, 3, 2
STATE = {}


def state():
    if not STATE:
        b = it.Board(N)
        span = it.closure(b, D, D - 1)
        VK = b.monomials(K)
        zero = it.Elim(b, span.index)
        CK = [it.mul({t}, b.Q(i)) for t in b.monomials(K - 1) for i in range(b.m)]
        CK += [{t} for t in VK if not b.matching(t)]
        STATE.update(b=b, span=span, VK=VK, zero=zero, CK=CK)
    return STATE


def error(b, a):
    return {b.var(1, j) for j in range(a)} | {b.var(2, j) for j in range(a, N)}


def shift(b, c):
    s = set()
    for i in [i for i, ci in enumerate(c) if ci]:
        s ^= b.Q(i)
    return s


def task(args):
    kind, a, cs = args
    s = state()
    E = error(s['b'], a)
    if kind == 'C':
        return it.kernel_dim(s['span'], E, s['VK'])
    return max(it.kernel_dim(s['zero'], E ^ shift(s['b'], c), s['VK'], s['CK']) for c in cs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    reps = list(itertools.product((0, 1), repeat=N + 1))
    chunks = [reps[k::12] for k in range(12)]
    with multiprocessing.Pool(14) as pool:
        out = {}
        for a in (0, 3):
            jobs = [('C', a, None)] + [('H', a, c) for c in chunks]
            res = pool.map(task, jobs)
            out[f'a={a}'] = {'C_side': res[0], 'best_H_side': max(res[1:]), 'excess': res[0] - max(res[1:])}
            print(f'7x6 D=3 K=2 a={a}', out[f'a={a}'], flush=True)
            pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
