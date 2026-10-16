"""Representative sums on the positive cases rep_sum.py did not cover, and the congruence of the tied pairs.

System: functional pigeonhole over F_2, n+1 pigeons, n holes, multilinear. Cases: the ten listed 5x4 hits on rows
{1,2} of row_search.json and the 5x4 partition error |A| = 2 (D=2, K=1, by rep_sum.py's pc_closure route);
the 7x6 partition error |A| = 3 at D=3, K=2 (by the independent route of independent_top.py, whose kernels are
here returned as bases built on tools/f2_span.py). For each, S(E) = sum over linear representatives E' of
Ann_H(E') cap V_K plus C cap V_K, against Ann_C(E) cap V_K; S(E) lies in Ann_C(E) by the containment of
lem:saving-monotonicity's proof, which this script also asserts in code (each basis vector of S kills E mod C).
Second: for the 12 pairs of pair_saving.json whose two savings tie at 6, whether the two errors are congruent
modulo span{Q_i} (then they have one kernel and the pair is a duplicate).
Statement tested: conj:representative-sum-transfer on these cases: dim S(E) = dim Ann_C(E).
Expected: no expectation is predicted for the sums; the reviewer's hand check predicts the 12 pairs congruent.
Refuted by: dim S(E) < dim Ann_C(E) for some case, or a tied pair whose errors are not congruent.
Possible because: the equality was computed at two sizes only, and the congruence on three of twelve pairs.
Control: S(x00) at 5x4 equals Ann_C(x00), single excess 0 there; asserted.
Refuted by: dim S(x00) different from dim Ann_C(x00).
Possible because: a bug in the sum of spaces or in the representatives.
Positive control: each listed hit has single excess 1 (row_search.json), so dim S > best single side is the effect
looked for; the script asserts the single excess 1 is reproduced before testing the sum.
Refuted by: a single excess other than 1 for a listed hit.
Possible because: a mismatch between this script's errors and row_search.py's.
Baseline: the single-representative excess bounds dim Ann_C - dim S above; it decides nothing.
Record checked: the claims read were conj:linear-kernel-transfer, lem:domain-model-stacked-rank and
lem:closure-degree-locality; none decides these sums.
"""
import argparse
import importlib.util
import itertools
import json
import multiprocessing
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import f2_span


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod             # so that worker processes can pickle its functions by name
    spec.loader.exec_module(mod)
    return mod


rs = load('rep_sum')
it = load('independent_top')
tq, dl = rs.tq, rs.dl


def kernel_basis(span, E, VK):
    """Basis (bit vectors over VK) of {u : uE in span}, by tagged elimination on f2_span."""
    img = {}
    out = []
    for k, t in enumerate(VK):
        x = span.reduce(span.vec(it.mul({t}, E)))
        tag = 1 << k
        while x:
            h = x.bit_length() - 1
            if h not in img:
                img[h] = (x, tag)
                break
            x ^= img[h][0]
            tag ^= img[h][1]
        if not x:
            out.append(tag)
    return out


STATE = {}


def state7():
    if not STATE:
        b = it.Board(6)
        span = it.closure(b, 3, 2)
        VK = b.monomials(2)
        zero = it.Elim(b, span.index)
        vk = {t: k for k, t in enumerate(VK)}
        CK = [it.mul({t}, b.Q(i)) for t in b.monomials(1) for i in range(b.m)]
        CK = [sum(1 << vk[t] for t in p) for p in CK] + [1 << vk[t] for t in VK if not b.matching(t)]
        STATE.update(b=b, span=span, VK=VK, zero=zero, CK=CK)
    return STATE


def part7(cs):
    s = state7()
    b = s['b']
    E = {b.var(1, j) for j in range(3)} | {b.var(2, j) for j in range(3, 6)}
    vecs = []
    for c in cs:
        q = set()
        for i in [i for i, ci in enumerate(c) if ci]:
            q ^= b.Q(i)
        vecs += kernel_basis(s['zero'], E ^ q, s['VK'])
    return list(f2_span.Span(vecs).piv.values())


def case7(pool):
    s = state7()
    b = s['b']
    E = {b.var(1, j) for j in range(3)} | {b.var(2, j) for j in range(3, 6)}
    reps = list(itertools.product((0, 1), repeat=7))
    parts = pool.map(part7, [reps[k::14] for k in range(14)])
    S = f2_span.Span([x for p in parts for x in p] + s['CK'])
    annC = kernel_basis(s['span'], E, s['VK'])
    A = f2_span.Span(annC)
    assert all(x in A for x in S.piv.values()), 'S inside Ann_C'
    return {'C_side': len(A), 'rep_sum': len(S), 'unexplained': len(A) - len(S)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = {}
    with multiprocessing.Pool(14) as pool:
        cC, cH, monos, CK, reps, v = rs.setup(4, 2, 1)
        name = lambda t: 0 if t == '1' else 1 << v(int(t[1]), int(t[2]))
        ctrl = rs.measure(pool, 4, 2, 1, {name('x00')})
        assert ctrl['rep_sum'] == ctrl['C_side'], 'control'
        out['5x4 x00'] = ctrl
        hits = json.loads((HERE / 'row_search.json').read_text())['5x4 rows [1, 2]']['first']
        cases = {'+'.join(h): {name(t) for t in h} for h in hits}
        cases['|A|=2'] = {name(f'x1{j}') for j in range(2)} | {name(f'x2{j}') for j in range(2, 4)}
        for key, E in cases.items():
            r = rs.measure(pool, 4, 2, 1, E)
            if key != '|A|=2':
                assert r['C_side'] - r['best_single'] == 1, 'positive control: single excess 1'
            out['5x4 ' + key] = r
        print('5x4', [(k, r['C_side'], r['best_single'], r['rep_sum']) for k, r in out.items()], flush=True)
        pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')
        out['7x6 |A|=3'] = case7(pool)
        print('7x6 |A|=3', out['7x6 |A|=3'], flush=True)
    b3 = it.Board(3)
    span_Q = f2_span.Span()
    vk = {t: k for k, t in enumerate(b3.monomials(1))}
    vec = lambda p: sum(1 << vk[t] for t in p)
    for i in range(4):
        span_Q.add(vec(b3.Q(i)))
    nm = lambda t: 0 if t == '1' else b3.var(int(t[1]), int(t[2]))
    ties = [r for r in json.loads((HERE / 'pair_saving.json').read_text())['pairs']
            if r['C_saving'] == 6 and r['domain_saving'] == 6]
    cong = [vec({nm(t) for t in r['pair'][0]} ^ {nm(t) for t in r['pair'][1]}) in span_Q for r in ties]
    out['tied_pairs'] = {'count': len(ties), 'congruent': sum(cong)}
    print('tied pairs', out['tied_pairs'], flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
