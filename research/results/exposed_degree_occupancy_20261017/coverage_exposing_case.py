"""No statement tested: runs tools/resemblance_coverage.py's check on the exposing draft (the first, reviewed draft
of the exposed degree occupancy entry, saved as exposing-draft.html beside this script) and on the corrected draft
(corrected-draft.html), against the real registry with each draft's own claims appended as registered last and
each spec's relationships, to show the check refuses the case that prompted it and passes its correction.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import resemblance_coverage as rc

HERE = Path(__file__).resolve().parent
reg = json.loads((ROOT / 'research/claims/index.json').read_text())
old = [{'id': 'lem:exposed-degree-occupancy', 'summary': (
    "Exposed degree occupancy: in lem:high-incidence-occupancy's charged character window (any graph, multigraphs "
    "included), for an edge set T, |T| = tau, K + tau <= D, 4K < m - tau, and a vertex set V_hi, let theta be the "
    "largest number of edges of T at a vertex outside V_hi, mu the largest number of edges off T joining a vertex "
    "outside V_hi to V_hi, h' the number of exposed vertices (those of V_hi with an edge off T), s_0 the least "
    "number of off-T edges at an exposed vertex and kappa the largest number of off-T edges joining an exposed "
    "vertex to V_hi. If theta + 2 mu < epsilon and s_0 > kappa, then q_T(K) >= (1 - eta_ex) B_(m-tau)(K) with "
    "eta_ex = (1 + 2 beta_T^(epsilon - theta - 2 mu))^n (1 + 2 beta_T^(s_0 - kappa))^(h') - 1, beta_T = 2 "
    "sqrt(K/(m - tau)): a potential's nonzero values at exposed vertices are charged by their own off-T edges, "
    "d'_s >= (epsilon - theta - 2 mu) sigma + (s_0 - kappa) xi, so a coset holds at most one good character and "
    "no factor 3^(h') is paid.")},
       {'id': 'cor:exposed-degree-tuple-ratio', 'summary': (
    "Exposed degree tuple ratio: in lem:local-tuple-ratio's setting (components E_i = P_i m_(gamma_i), P_i "
    "functions of the states of T, e_max + K <= D, K + tau + |supp gamma_i| <= D), with c(K) > 0, 4K < m - tau "
    "and lem:exposed-degree-occupancy's hypotheses with eta_ex < 1, c(K-d)/c(K) <= (1 - eta_ex)^(-1) "
    "B_(m-tau)(K-d)/B_(m-tau)(K) for 0 <= d <= K. On the power-growing charged family, for tau <= D - K, theta + 2 "
    "mu <= Delta/8 and s_0 - kappa >= Delta/8, the factor is below 1.5 for large n and any number h' <= n of "
    "exposed vertices.")}]
old_rel = ([('lem:exposed-degree-occupancy', 'cites', x)
            for x in ('lem:high-incidence-occupancy', 'lem:exposed-vertex-occupancy', 'lem:pin-rank-transfer')]
           + [('cor:exposed-degree-tuple-ratio', 'cites', x)
              for x in ('lem:local-tuple-ratio', 'lem:exposed-degree-occupancy', 'lem:ball-ratio-comparison',
                        'prop:charge-affine-rank-gap')])
spec = json.loads((HERE / 'claim-spec.json').read_text())


def edges(pairs):
    return [{'source': {'id': a}, 'target': {'id': b}, 'type': t} for a, t, b, *_ in pairs]


for label, name, own, rel in (('exposing draft', 'exposing-draft.html', old, old_rel),
                              ('corrected draft', 'corrected-draft.html', spec['claims'], spec['relationships'])):
    gaps = rc.missing((HERE / name).read_text(), reg['claims'] + own,
                      relationships=reg['relationships'] + edges(rel))
    print(label + ': ' + ('; '.join(f'{o} {s:.2f} beside {i}' for i, s, o in gaps) or 'passes'))
