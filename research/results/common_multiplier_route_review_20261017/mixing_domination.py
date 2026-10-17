"""Is the 4x3 pair survivor dominated: is J = Ann_C(s) cap V_1 for one s of degree <= D - K = 1?

System and pairs as in mixing_pairs.py (functional pigeonhole over F_2, 4 pigeons, 3 holes, D = 2, K = 1; the 33
non-congruent pairs of the ten positive-excess errors). The open statement excludes a common kernel shown to be
the annihilator of one element of the window (lem:factor-ideal-domination); with K = 1 and D = 2 the window for
the element is degree <= D - K = 1, so all 2^13 elements s of V_1 are tried.
Statement tested: the untested hypothesis that the survivor of mixing_pairs.json is dominated, J = Ann_C(s) cap V_1
for some s in V_1, on every non-congruent pair.
Expected: no expectation is predicted; the script prints, per pair, the number of s with Ann_C(s) cap V_1 = J.
Refuted by: a pair with no such s, whose survivor is then not shown dominated at this degree.
Possible because: J has dimension 5 while each listed error has a kernel of dimension 7, so a single s must have a
smaller kernel than any listed error, which the errors' own kernels do not supply.
Control: for a congruent pair (E, E + member of span{Q_i}), s = E gives Ann_C(s) cap V_1 = J; asserted.
Refuted by: no s found on a congruent pair.
Possible because: a wrong kernel comparison would miss it.
Forced by counts: nothing forces the count of s; 8192 elements against one 5-dimensional target.
Positive control: for a chosen s0 whose kernel has dimension 5, J0 = Ann_C(s0) cap V_1 is computed afresh as an
intersection, the way J is, and the matching path must list s0 among its matches; asserted. (Third run. The
congruent-pair control above holds by definition and does not pass through the matching path, and the second
run's control matched a table kernel against itself, failing only if space addition were broken; the reviewer's
follow-up found both unable to fail.)
Refuted by: s0 missing from the matches for its own freshly computed kernel.
Possible because: a key built from a basis in another order, or a wrong span comparison, would miss it.
Baseline: dim Ann_C(s) is at least dim W = 4 for every s; it decides nothing.
Record checked: lem:factor-ideal-domination (the clause's form) and mixing_pairs.json; none gives the s.
"""
import argparse
import importlib.util
import itertools
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('mixing_pairs', HERE / 'mixing_pairs.py')
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)
pc, tq, dl = mp.pc, mp.tq, mp.dl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    mono, full, nv, v = tq.systems(mp.N + 1, mp.N)
    cC = tq.prepare(pc.Closure(full, nv, 2))
    monos = [x for x in cC.monos if tq.deg(x) <= 1]
    assert len(monos) == 13
    # the kernel of every s in V_1, keyed by its basis, computed once
    kernels = {}
    for bits in range(1, 1 << len(monos)):
        s = {monos[k] for k in range(len(monos)) if bits >> k & 1}
        K = dl.ann_poly(cC, monos, s)
        kernels.setdefault(frozenset(K.basis.values()) if len(K) == 5 else None, []).append(sorted(s))
    # positive control of the matching path: for a chosen s0 with a 5-dimensional kernel, J0 = Ann_C(s0) cap V_1 is
    # computed afresh as an intersection, the way J is, and the matching path must count s0 among its matches
    s0 = next(ss for key, ss in kernels.items() if key is not None)[0]
    J0 = dl.ann_poly(cC, monos, set(s0)) & dl.ann_poly(cC, monos, set(s0))
    matched = [s for key, ss in kernels.items() if key is not None and len(tq.Space(list(key)) + J0) == 5 for s in ss]
    assert s0 in matched, 'positive control: the matching path misses s0'
    Q = [{0} | {1 << v(i, j) for j in range(mp.N)} for i in range(mp.N + 1)]
    span_Q = {frozenset(sh) for _, sh in mp.ls.representatives(Q)}
    hits = json.loads((mp.SRC / 'row_search.json').read_text())['4x3 rows [1, 2]']['first']
    errors = [{mp.parse(t, v) for t in E} for E in hits]
    rows, found_counts = [], {}
    for i, j in itertools.combinations(range(10), 2):
        J = dl.ann_poly(cC, monos, errors[i]) & dl.ann_poly(cC, monos, errors[j])
        congruent = frozenset(errors[i] ^ errors[j]) in span_Q
        if congruent:
            assert len(dl.ann_poly(cC, monos, errors[i]) + J) == len(J), 'control: s = E dominates'
            continue
        assert len(J) == 5
        # spaces compare by span: an s dominates when its kernel and J have the same span
        count = sum(len(ss) for key, ss in kernels.items()
                    if key is not None and len(tq.Space(list(key)) + J) == 5)
        rows.append({'pair': [hits[i], hits[j]], 'dominating_s': count})
        found_counts[count] = found_counts.get(count, 0) + 1
    out = {'s_tried': (1 << len(monos)) - 1, 's_with_kernel_dim_5': sum(len(ss) for key, ss in kernels.items() if key),
           'pairs_by_number_of_dominating_s': found_counts, 'pairs': rows}
    print(json.dumps({k: out[k] for k in ('s_tried', 's_with_kernel_dim_5', 'pairs_by_number_of_dominating_s')}),
          flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
