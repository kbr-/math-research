"""Instance (ii) of the window review's Decisive test: six pigeons, five holes, D = 3, K = 2, partition-error pairs.

System: functional pigeonhole over F_2, 6 pigeons, 5 holes, multilinear. Errors E_A = sum_{j in A} x_1j +
sum_{j not in A} x_2j, |A| in {2, 3}; the holes' symmetry acts on A, so a pair's quantities depend only on
(|A|, |B|, |A cap B|), and one pair per orbit (A not equal to B) is computed. Quantities as in mixing_pairs.py:
J, W = C cap V_2, a (best single representative pair), b (sum over representative pairs), I (intersection of the
per-error representative sums), each a maximum or a sum because the question is the largest part explained.
Statement tested: whether the four-pigeon intersection survivor persists here: b < dim J on some orbit.
Expected: no outcome is predicted; dim J = I is expected on every orbit (rep_sum.json gives each single kernel as
its representative sum at |A| = 2, 3, and the symmetry carries it to every A of those sizes); the script asserts
it.
Refuted by: dim J different from I on some orbit, which would contradict rep_sum.json's equality carried by
symmetry.
Possible because: the symmetry argument assumes the closure and the representative set are permuted by hole
permutations, which a bug in either construction would break.
Control: for the single error E_{0,1}, dim Ann_C = 332 and the representative sum 332 (rep_sum.json); asserted.
(Corrected after the run: an earlier wording also listed dim W as asserted, which the code does not do; dim W = 276
is asserted by dims_65.py.)
Refuted by: either figure different.
Possible because: a wrong closure or degree would change them.
Forced by counts: nothing forces 332; the closure's degree-two part is computed.
No positive control: no orbit is known in advance to have b < dim J; the four-pigeon run (mixing_pairs.json) is
this computation's positive control on its own board.
Baseline: a <= b <= I <= dim J; they decide nothing about the gaps.
Record checked: the claims read were check:top-degree-partition-kernels and conj:representative-sum-transfer,
with mixing_pairs.json and mixing_domination.json; none gives a, b or I at this board.
Decisive at these sizes: exact dimensions, no seeds; one orbit with b below dim J, by one dimension or more, decides.
Parallel use: fourteen worker processes, one per representative of the first error, one thread each; the
measured time per orbit is printed (the window review's Attempt clause asks for the step's measured cost).
"""
import argparse
import importlib.util
import itertools
import json
import multiprocessing
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import pc_closure as pc

SRC = ROOT / 'research/results/common_multiplier_linear_sizes_20261017'
spec = importlib.util.spec_from_file_location('linear_sizes', SRC / 'linear_sizes.py')
ls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls)
tq, dl = ls.tq, ls.dl
N, D, K = 5, 3, 2
STATE = {}


def setup():
    if not STATE:
        mono, full, nv, v = tq.systems(N + 1, N)
        cC = tq.prepare(pc.Closure(full, nv, D))
        cH = tq.prepare(pc.Closure(mono, nv, D))
        monos = [x for x in cC.monos if tq.deg(x) <= K]
        W = tq.members(cC, monos)
        Q = [{0} | {1 << v(i, j) for j in range(N)} for i in range(N + 1)]
        STATE.update(cC=cC, cH=cH, monos=monos, W=W, reps=ls.representatives(Q), v=v)
    return STATE


def error(A):
    v = setup()['v']
    return {1 << v(1, j) for j in A} | {1 << v(2, j) for j in range(N) if j not in A}


def domain_kernels(E):
    st = setup()
    return [dl.ann_poly(st['cH'], st['monos'], set(E) ^ s) for _, s in st['reps']]


def row(args):
    """For one representative of the first error: the best and the sum over the second error's representatives."""
    # spaces travel as basis lists: three_quantities is loaded by path, so its Space does not pickle
    h1, h2s, W = tq.Space(args[0]), [tq.Space(x) for x in args[1]], tq.Space(args[2])
    best, total = 0, tq.Space()
    for h2 in h2s:
        x = h1 & h2
        best = max(best, len(x + W))
        total = total + x
    return best, list(total.basis.values())


def joined(parts, W):
    return tq.Space([x for _, vecs in parts for x in vecs]) + W


def summed(spaces, W):
    total = tq.Space() + W
    for x in spaces:
        total = total + x
    return total


def measure_orbit(pool, key, A, B):
    st = setup()
    cC, monos, W = st['cC'], st['monos'], st['W']
    t0 = time.time()
    E1, E2 = error(A), error(B)
    J = dl.ann_poly(cC, monos, E1) & dl.ann_poly(cC, monos, E2)
    h1s, h2s = domain_kernels(E1), domain_kernels(E2)
    lists = [list(x.basis.values()) for x in h2s]
    parts = pool.map(row, [(list(h1.basis.values()), lists, list(W.basis.values())) for h1 in h1s])
    a = max(p[0] for p in parts)
    total = joined(parts, W)
    I = summed(h1s, W) & summed(h2s, W)
    r = {'sizes_and_overlap': key, 'A': A, 'B': B, 'J': len(J), 'a': a, 'b': len(total), 'I': len(I),
         'seconds': round(time.time() - t0, 1)}
    assert r['a'] <= r['b'] <= r['I'] <= r['J'], f'containments {r}'
    assert r['J'] == r['I'], f'J = I expected from rep_sum.json and symmetry: {r}'
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    st = setup()
    cC, monos, W = st['cC'], st['monos'], st['W']
    single = dl.ann_poly(cC, monos, error((0, 1)))
    k01 = domain_kernels(error((0, 1)))
    S01 = tq.Space() + W
    for x in k01:
        S01 = S01 + x
    assert len(single) == 332 == len(S01), f'control: {len(single)}, {len(S01)}'
    orbits = {}
    subsets = list(itertools.chain(itertools.combinations(range(N), 2), itertools.combinations(range(N), 3)))
    for A, B in itertools.product(((0, 1), (0, 1, 2)), subsets):
        if B != A:
            orbits.setdefault((len(A), len(B), len(set(A) & set(B))), (A, B))
    out = {'dim_W': len(W), 'single_C_side': len(single), 'orbits': []}
    with multiprocessing.Pool(14) as pool:
        for key, (A, B) in sorted(orbits.items()):
            r = measure_orbit(pool, key, A, B)
            out['orbits'].append(r)
            print(json.dumps(r), flush=True)
            pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
