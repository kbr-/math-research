"""The two-level chain on the box-level samples: does some maximum matching of G_2 contain a maximum matching of G_1?

Outcome (18 October 2026): the controls pass (the gadget gives e = 2 > d = 1, equal levels e = 0), and no sample
finished: scipy's min_weight_full_bipartite_matching did not solve the first 4096-point sample in 110 s, twice,
nor with tie-breaking jitter in 100 s (run1-unfinished.txt, run2-unfinished.txt, profile-jittered-unfinished.txt;
profile.py times the steps before the solver at under 0.1 s). The run was not continued: an exact answer needs a
compiled min-cost-flow kernel, and it would bear on L = 1/2 only, below the admissible constants.

With --terms (written before that run, 18 October 2026): lem:two-level-chain-criterion's necessary terms F = E'
and F = empty, r*_X(T_X) >= d and r*_Y(T_Y) >= d, and its Konig relaxation nuD >= d, on the nine saved samples
(N in {4096, 16384, 65536}); each failing term refutes the chain. Expected: refuted at N = 16384, seed 1 (nuD <
d there); at the other eight, no expectation either way. Control: the entry's instance (b), where rX = 1 < d = 2
while nuD = 2 (Forced by counts: its three vertices a side force both values). Refuted by: a sample with
refuted False at N = 16384, seed 1. Possible because: an error in the dual rank or the free sets would show so.

Statement tested (finite check): at (4,4), X uniform and Y evenly spread (box_completion.py's sample), box graphs
G_k of the pairs within L k^(1/4) sqrt(log N/N) in both coordinates, at L = 1/2, N in {4096, 16384}, seeds 0, 1, 2:
the chain at levels 1, 2 holds exactly when the least number of edges outside G_1 in a maximum matching of G_2
equals d = nu(G_2) - nu(G_1). Computed exactly as a minimum-weight full matching (scipy's
min_weight_full_bipartite_matching): G_1 edges cost 1, the edges G_2 adds cost 2, and m_2 dummy rows and m_2 dummy
columns, joined at cost B = 3 to the columns and rows of G_2 that some maximum matching leaves free and not to each
other, force a real matching of size nu(G_2); its cost is nu(G_2) + e + 2 m_2 B, e the edges outside G_1, so e is
read off (the real edges of cost 2) and the chain holds iff e = d.
The least e over maximum matchings: the extreme the question needs, since the chain asks for one such matching.

Expected (written before the run): at N = 16384, seed 1, where lem:completion-failure-certificate's second test
fires (research/results/ultimate_matching_layered_cost_20261018/second_test_rows.txt), e > d; at the other
samples, no expectation either way: the second test does not fire there, and the chain may hold or fail.
Positive control: the gadget G_1 = {x1y1}, G_2 = G_1 + {x1y2, x2y1}, where the chain fails (e = 2 > d = 1), and the
seed-1 sample at N = 16384, where the second test forces failure; both must print chain False.
Refuted by: a chain True at N = 16384, seed 1, which would contradict the certificate's second test there.
Possible because: the second test is a proved refutation, so this output would show an error in the matching
code or in its reading of the dummy construction, which is what the control is for.
Control: a pair G_1 = G_2 (no drop), where e = d = 0 must hold; and each sample's nu(G_2) recomputed by the
Hopcroft-Karp kernel of box_completion.py and asserted equal to the real matching size of the weighted solution.
Each sample's m_1 and m_2 are asserted equal to those box_completion.py saved for the same N and seed.
Forced by counts: G_1 = G_2 forces e = 0 (no edge lies outside G_1), the gadget's unique maximum matching of G_2
forces e = 2, and the seed-1 sample's nu(G_2[D_X u D_Y]) = 108 < d = 134 forces e > d; each control so tests
only the routine (the dummy construction, the cost offsets, the sample's reconstruction), not the question.
Refuted by: a mismatch between the two nu(G_2) values, or e != 0 when G_1 = G_2.
Possible because: a wrong dummy count or a cost read with the wrong offset gives either.
Baseline: the second test of lem:completion-failure-certificate, nu(G_2[D_X u D_Y]) >= d, necessary for the chain;
it decides the seed-1 sample at N = 16384 and leaves the other eight open, which this run decides.
Record checked: lem:completion-failure-certificate, thm:universal-completion-criterion (a) (co-basis pairs) and
ex:box-completion-failures (the same samples) were read for whether together they decide the outcome; they decide
only the seed-1 sample.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix, coo_matrix
from scipy.sparse.csgraph import min_weight_full_bipartite_matching

HERE = Path(__file__).resolve().parent
BOX = HERE.parent / 'ultimate_matching_box_completion_20261018' / 'box_completion.py'
spec = importlib.util.spec_from_file_location('box_completion', BOX)
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)
B = 3   # any constant above 2: the dummy edges' total is fixed, and the value only tells them apart from real ones


def least_outside(A1, A2):
    """(nu(G_2), least number of edges outside G_1 in a maximum matching of G_2) by the dummy construction."""
    n1, n2 = A2.shape
    A2 = csr_matrix(A2)
    rmate, cmate = bc.match(A2)
    nu2 = int((rmate >= 0).sum())
    mx, my = n1 - nu2, n2 - nu2          # unmatched rows and columns of a maximum matching of G_2
    # A column matched to a dummy row is left free by the real part, a maximum matching of G_2, so it is missable
    # in G_2 (bc.missable_columns); joining the dummies only to missable vertices keeps every solution. Every full
    # matching uses exactly my + mx dummy edges, so their cost is a constant, B = 3 (a first version joined them to
    # every vertex at 10^6 and did not finish one sample of 4096 points in 110 s).
    DY = np.nonzero(bc.missable_columns(A2, rmate, cmate))[0]
    DX = np.nonzero(bc.missable_columns(A2.T.tocsr(), cmate, rmate))[0]
    A2 = coo_matrix(A2)
    in1 = np.asarray(csr_matrix(A1)[A2.row, A2.col]).ravel() > 0
    rows = [A2.row, np.repeat(np.arange(n1, n1 + my), len(DY)), np.tile(DX, mx)]
    cols = [A2.col, np.tile(DY, my), np.repeat(np.arange(n2, n2 + mx), len(DX))]
    wts = [np.where(in1, 1.0, 2.0), np.full(my * len(DY), float(B)), np.full(mx * len(DX), float(B))]
    W = csr_matrix((np.concatenate(wts), (np.concatenate(rows), np.concatenate(cols))),
                   shape=(n1 + my, n2 + mx))
    r, c = min_weight_full_bipartite_matching(W)
    w = np.asarray(W[r, c]).ravel()
    real = w < B
    assert int(real.sum()) == nu2, (int(real.sum()), nu2)
    return nu2, int((w[real] == 2.0).sum())


def necessary_terms(A1, A2):
    """lem:two-level-chain-criterion's terms F = E' and F = empty, each a necessary condition for the chain:
    rX = r*_X(T_X) and rY = r*_Y(T_Y), T_X, T_Y the ends of the G_2 edges between the free sets D_X, D_Y of G_1,
    r*_X(S) = |S| - nu(G_1) + nu(G_1 - S); also nuD = nu(G_2[D_X, D_Y]), the Konig relaxation."""
    A1 = csr_matrix(A1)
    rmate, cmate = bc.match(A1)
    nu1 = int((rmate >= 0).sum())
    DY = bc.missable_columns(A1, rmate, cmate)
    DX = bc.missable_columns(A1.T.tocsr(), cmate, rmate)
    E = csr_matrix(A2)[DX][:, DY]
    TX = np.zeros(A1.shape[0], bool); TX[np.nonzero(DX)[0][np.unique(E.nonzero()[0])]] = True
    TY = np.zeros(A1.shape[1], bool); TY[np.nonzero(DY)[0][np.unique(E.nonzero()[1])]] = True
    nu = lambda A: int((bc.maximum_bipartite_matching(A) >= 0).sum()) if A.nnz else 0
    rX = int(TX.sum()) - nu1 + nu(A1[~TX])
    rY = int(TY.sum()) - nu1 + nu(A1[:, ~TY])
    return dict(DX=int(DX.sum()), DY=int(DY.sum()), TX=int(TX.sum()), TY=int(TY.sum()), rX=rX, rY=rY, nuD=nu(E))


def controls():
    out = {}
    A1 = csr_matrix(np.array([[1, 0], [0, 0]]))
    A2 = csr_matrix(np.array([[1, 1], [1, 0]]))
    nu1 = int((bc.maximum_bipartite_matching(A1) >= 0).sum())
    nu2, e = least_outside(A1, A2)
    out['gadget'] = dict(nu1=nu1, nu2=nu2, d=nu2 - nu1, e=e, chain=e == nu2 - nu1)
    assert out['gadget']['chain'] is False
    nu2, e = least_outside(A2, A2)
    out['equal_levels'] = dict(nu=nu2, e=e)
    assert e == 0
    # Instance (b) of the entry: the F = E' term is 1 < d = 2 while nuD = 2 >= d.
    B1 = csr_matrix(np.array([[1, 0, 0], [1, 0, 0], [0, 0, 0]]))
    B2 = csr_matrix(np.array([[1, 1, 0], [1, 0, 1], [1, 0, 0]]))
    t = necessary_terms(B1, B2)
    out['instance_b'] = t
    assert (t['rX'], t['nuD']) == (1, 2), t
    return out


def run_terms(N, L, seed):
    """The necessary terms at levels 1 and 2 of a saved sample."""
    rng = np.random.default_rng(seed)
    X = rng.uniform(0, 1, (N, 2))
    g = int(round(math.sqrt(N)))
    cells = np.stack(np.meshgrid(np.arange(g), np.arange(g), indexing='ij'), -1).reshape(-1, 2)
    Y = (cells + rng.uniform(0, 1, (N, 2))) / g
    s1 = math.sqrt(math.log(N) / N)
    A1, A2 = bc.graph(X, Y, L * s1), bc.graph(X, Y, L * 2 ** 0.25 * s1)
    m1 = N - int((bc.maximum_bipartite_matching(A1) >= 0).sum())
    m2 = N - int((bc.maximum_bipartite_matching(A2) >= 0).sum())
    t = necessary_terms(A1, A2)
    d = m1 - m2
    return dict(N=N, L=L, seed=seed, m1=m1, m2=m2, d=d, **t,
                refuted=bool(t['rX'] < d or t['rY'] < d or t['nuD'] < d))


def run(N, L, seed):
    rng = np.random.default_rng(seed)             # the same draws, in the same order, as box_completion.sample
    X = rng.uniform(0, 1, (N, 2))
    g = int(round(math.sqrt(N)))
    cells = np.stack(np.meshgrid(np.arange(g), np.arange(g), indexing='ij'), -1).reshape(-1, 2)
    Y = (cells + rng.uniform(0, 1, (N, 2))) / g
    s1 = math.sqrt(math.log(N) / N)
    A1, A2 = bc.graph(X, Y, L * 1 * s1), bc.graph(X, Y, L * 2 ** 0.25 * s1)
    nu1 = int((bc.maximum_bipartite_matching(A1) >= 0).sum())
    nu2, e = least_outside(A1, A2)
    return dict(N=N, L=L, seed=seed, m1=N - nu1, m2=N - nu2, d=nu2 - nu1, e=e, chain=e == nu2 - nu1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--sizes', type=int, nargs='+', default=[4096, 16384])
    ap.add_argument('--terms', action='store_true', help='only the necessary terms, at every saved size')
    args = ap.parse_args()
    result = dict(controls=controls(), samples=[])
    print(json.dumps(result['controls']), flush=True)
    if args.terms:
        for N in args.sizes:
            for seed in (0, 1, 2):
                row = run_terms(N, 0.5, seed)
                result['samples'].append(row)
                print(json.dumps(row), flush=True)
                Path(args.out).write_text(json.dumps(result, indent=1))
        hit = [r for r in result['samples'] if r['N'] == 16384 and r['seed'] == 1]
        assert not hit or hit[0]['refuted'], 'the second test refutes the chain at N = 16384, seed 1'
        return
    saved = {}
    for f in ('box_completion_4096.json', 'box_completion.json'):
        for s in json.loads((BOX.parent / f).read_text())['samples']:
            if len(s['levels']) >= 2:
                saved[(s['N'], s['seed'])] = (s['levels'][0]['m'], s['levels'][1]['m'])
    for N in args.sizes:
        for seed in (0, 1, 2):
            row = run(N, 0.5, seed)
            # The same sample as the saved run: its deficiencies at levels 1 and 2 must agree.
            assert (N, seed) not in saved or saved[(N, seed)] == (row['m1'], row['m2']), (saved.get((N, seed)), row)
            result['samples'].append(row)
            print(json.dumps(row), flush=True)
            Path(args.out).write_text(json.dumps(result, indent=1))
    hit = [r for r in result['samples'] if r['N'] == 16384 and r['seed'] == 1]
    assert not hit or hit[0]['chain'] is False, 'the second test refutes the chain at N = 16384, seed 1'


if __name__ == '__main__':
    main()
