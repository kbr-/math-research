"""Controls of box_completion.py's failure certificate, run on their own (seconds).

No statement tested: these are the controls of box_completion.py, whose docstring states the
statement, the expectations and the refuting outputs; they moved here so that the long run of the
samples holds no brute-force loop.
Control: soundness on tiny line instances (n = 4 and 5 per side, radii 1 and e), every maximum
matching enumerated: the certificate and the second test must never fire where universal completion
holds.
Positive control: the line gadget X = {0, 1.6}, Y = {0.8, 3.5}, where it fails and the certificate
must fire.
Refuted by: the certificate firing on a tiny instance where brute force finds completion.
Possible because: an error in the alternating reachability or the matchability test would show.
Kernel control: the compiled matching's size against networkx on 200 random
bipartite graphs.
Forced by counts: as in box_completion.py, the counts force only which instances have a drop.
"""
import argparse
import itertools
import json
import math

import numpy as np
from scipy.sparse import csr_matrix

from box_completion import certificate, graph, maximum_bipartite_matching


def brute_universal(adj_k, adj_k1, n):
    """Universal completion at one level by enumerating every maximum matching (tiny n)."""
    def matchings(adj):
        edges = [(i, j) for i in range(n) for j in range(n) if adj[i][j]]
        best, found = 0, [()]
        for size in range(1, n + 1):
            cur = [c for c in itertools.combinations(edges, size)
                   if len({e[0] for e in c}) == size and len({e[1] for e in c}) == size]
            if not cur:
                break
            best, found = size, cur
        return best, found
    nu_k, maxk = matchings(adj_k)
    nu_k1, _ = matchings(adj_k1)
    d = nu_k1 - nu_k
    for M in maxk:
        ux = [i for i in range(n) if i not in {e[0] for e in M}]
        uy = [j for j in range(n) if j not in {e[1] for e in M}]
        sub = [[adj_k1[i][j] for j in uy] for i in ux]
        best = 0
        for size in range(1, min(len(ux), len(uy)) + 1):
            if any(all(sub[a][b] for a, b in zip(rows, cols))
                   for rows in itertools.combinations(range(len(ux)), size)
                   for cols in itertools.permutations(range(len(uy)), size)):
                best = size
        if best < d:
            return False
    return True


def line_instance(x, y, radii):
    X = np.column_stack([x, np.zeros(len(x))])
    Y = np.column_stack([y, np.zeros(len(y))])
    return [graph(X, Y, r) for r in radii]


def controls(rng):
    out = {}
    gk, gk1 = line_instance([0, 1.6], [0.8, 3.5], [1.0, math.e])
    nu, det = certificate(gk, gk1)
    out['gadget'] = dict(nu_k=nu, **det)
    sound = dict(instances=0, drops=0, universal_fails=0, cert_fires=0, cert_fires_where_holds=0,
                 nuD_fires=0, nuD_fires_where_holds=0)
    for n, reps in ((4, 1500), (5, 300)):
        for _ in range(reps):
            x, y = rng.uniform(0, n, n), rng.uniform(0, n, n)
            gk, gk1 = line_instance(x, y, [1.0, math.e])
            nu_k, det = certificate(gk, gk1)
            nu_k1 = int((maximum_bipartite_matching(gk1, perm_type='column') >= 0).sum())
            sound['instances'] += 1
            if nu_k1 == nu_k:
                continue
            sound['drops'] += 1
            ak = (gk.toarray() > 0).tolist()
            ak1 = (gk1.toarray() > 0).tolist()
            holds = brute_universal(ak, ak1, n)
            sound['universal_fails'] += (not holds)
            sound['cert_fires'] += det['cert']
            sound['cert_fires_where_holds'] += (det['cert'] and holds)
            nuD = det['nuD'] < nu_k1 - nu_k
            sound['nuD_fires'] += nuD
            sound['nuD_fires_where_holds'] += (nuD and holds)
    out['soundness'] = sound
    import networkx as nx
    agree = 0
    for rep in range(200):
        n = int(rng.integers(20, 200))
        A = csr_matrix((rng.random((n, n)) < rng.uniform(0.005, 0.05)).astype(np.int8))
        G = nx.algorithms.bipartite.from_biadjacency_matrix(A)
        ref = len(nx.bipartite.maximum_matching(G, top_nodes=range(n))) // 2
        agree += int((maximum_bipartite_matching(A) >= 0).sum()) == ref
    out['kernel_against_networkx'] = dict(graphs=200, agree=agree)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    c = controls(np.random.default_rng(20261018))
    with open(args.out, 'w') as f:
        json.dump(c, f, indent=1)
    print('controls', json.dumps(c))
    assert c['gadget']['cert'], c['gadget']
    assert c['soundness']['cert_fires_where_holds'] == 0, c['soundness']
    assert c['soundness']['nuD_fires_where_holds'] == 0, c['soundness']
    assert c['kernel_against_networkx']['agree'] == 200, c['kernel_against_networkx']


if __name__ == '__main__':
    main()
