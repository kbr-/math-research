"""Additivity of the deficit-first divisible sandpile's net flow on a cycle of four cells.

Statement tested: the net flow F(e) of the deficit-first rule below, as a function of the excess e = eta - t, is
not additive: some e1, e2 have F(e1 + e2) != F(e1) + F(e2).  The balanced-sandpile lemma (lem:balanced-sandpile-flow)
shows every balanced odometer of a fixed splitting kernel gives the electrical flow, which is linear; this rule's
splitting depends on the state, so the lemma does not apply, and the entry that named the attempt asked for the rule
to be fully defined and a failure of additivity exhibited before calling it nonlinear.

Rule (exact rational arithmetic): scan the sites in index order; the first site x with eta(x) > t(x) has excess
e = eta(x) - t(x); D = its neighbours y with eta(y) < t(y), deficits d(y) = t(y) - eta(y).  If D is nonempty and
e <= sum d, x sends e d(y)/sum d to each y in D; if e > sum d it sends d(y) to each y in D and splits the rest
equally among all its neighbours; if D is empty it splits e equally among all neighbours.  Repeat until every site
is at most its threshold, or a step limit is reached (then the run is reported unstabilized and not used).

Expected before the run: the electrical flow is additive (it is linear), so it is the control; the deficit-first
flow F has F(e1 + e2) != F(e1) + F(e2) for e1 = (2, 0, -1, -1) and e2 = (0, 2, -1, -1), where for e1 cell 2 is at its
threshold and receives nothing in the first step, while for e1 + e2 both cells 1 and 2 are above it.
Refuted by: the computed deficit-first flows satisfying F(e1 + e2) = F(e1) + F(e2) on every listed pair of inputs.
Possible because: a state-dependent rule can still produce flows that happen to add on these few inputs, for example
if every run sends all mass straight to the cells in deficit.
Control: the electrical flow, computed by solving the cycle's Laplacian, must be additive on the same pairs.
Positive control: the deficit-first flow of the record's case (3, 1, 0, 0), thresholds 1, must differ from the
electrical flow (1.25 on edge 1-4, 0.75 on edge 1-2) by a circulation, as the balanced-sandpile entry found by hand.
Forced by counts: the electrical control is additive by linearity whatever the inputs, so it tests only the solver;
the positive control's difference is divergence-free by mass conservation, so only "differs" can fail there.
Baseline: the plainest bound is the lemma's statement that any two flows with the same divergence differ by a
circulation; it does not decide additivity, which is a property of the rule across inputs.
Record checked: lem:balanced-sandpile-flow (linear for fixed kernels) and the balanced-sandpile entry's Suggestion
checked paragraph (the four-cycle case); a search "slack sandpile threshold no cell topples Chernoff cell counts
electrical flow state-dependent rule nonlinear additivity" found no claim deciding it.
"""
import argparse
import json
from fractions import Fraction as Fr

EDGES = [(0, 1), (1, 2), (2, 3), (3, 0)]                       # the cycle 1-2-3-4, indices from 0
NEIGHBOURS = {x: [b if a == x else a for a, b in EDGES if x in (a, b)] for x in range(4)}


def deficit_first(excess, limit=10000):
    """Net flow on each edge (a, b), positive from a to b, and the number of steps; None if not stabilized."""
    eta = [Fr(e) for e in excess]                                  # thresholds 0: eta is the excess itself
    flow = {edge: Fr(0) for edge in EDGES}

    def send(x, y, amount):
        eta[x] -= amount
        eta[y] += amount
        if (x, y) in flow:
            flow[(x, y)] += amount
        else:
            flow[(y, x)] -= amount

    for step in range(limit):
        over = [x for x in range(4) if eta[x] > 0]
        if not over:
            return flow, step
        x = over[0]
        e = eta[x]
        deficits = {y: -eta[y] for y in NEIGHBOURS[x] if eta[y] < 0}
        total = sum(deficits.values(), Fr(0))
        if deficits and e <= total:
            for y, d in deficits.items():
                send(x, y, e * d / total)
        else:
            for y, d in deficits.items():
                send(x, y, d)
            rest = e - total
            for y in NEIGHBOURS[x]:
                send(x, y, rest / len(NEIGHBOURS[x]))
    return None, limit


def electrical(excess):
    """The electrical flow on the four-cycle: potentials u with Laplacian u = excess, flow u(a) - u(b)."""
    # Solve on the cycle with u(3) = 0 by Gaussian elimination in fractions.
    lap = [[Fr(0)] * 4 for _ in range(4)]
    for a, b in EDGES:
        lap[a][a] += 1
        lap[b][b] += 1
        lap[a][b] -= 1
        lap[b][a] -= 1
    rows = [lap[i][:3] + [Fr(excess[i])] for i in range(3)]
    for c in range(3):
        p = next(r for r in range(c, 3) if rows[r][c] != 0)
        rows[c], rows[p] = rows[p], rows[c]
        for r in range(3):
            if r != c and rows[r][c] != 0:
                f = rows[r][c] / rows[c][c]
                rows[r] = [u - f * v for u, v in zip(rows[r], rows[c])]
    u = [rows[i][3] / rows[i][i] for i in range(3)] + [Fr(0)]
    return {(a, b): u[a] - u[b] for a, b in EDGES}


def add(f, g):
    return {k: f[k] + g[k] for k in f}


def show(f):
    return {f'{a + 1}-{b + 1}': str(v) for (a, b), v in f.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    pairs = [((2, 0, -1, -1), (0, 2, -1, -1)), ((2, 0, -1, -1), (-1, -1, 2, 0)), ((2, -1, 0, -1), (0, -1, 2, -1))]
    report = {'pairs': []}
    positive = deficit_first((2, 0, -1, -1))[0]
    elec = electrical((2, 0, -1, -1))
    circulation = {k: positive[k] - elec[k] for k in EDGES}
    divergence_free = all(sum(circulation[e] if e[0] == x else -circulation[e] for e in EDGES if x in e) == 0
                          for x in range(4))
    report['positive_control'] = {'deficit_first': show(positive), 'electrical': show(elec),
                                  'difference_is_circulation': divergence_free,
                                  'differs': positive != elec}
    print('positive control: deficit-first', show(positive), 'electrical', show(elec),
          'difference divergence-free:', divergence_free)
    assert divergence_free and positive != elec
    for e1, e2 in pairs:
        s = tuple(a + b for a, b in zip(e1, e2))
        f1, n1 = deficit_first(e1)
        f2, n2 = deficit_first(e2)
        fs, ns = deficit_first(s)
        assert f1 is not None and f2 is not None and fs is not None, 'a run did not stabilize'
        additive = fs == add(f1, f2)
        el_additive = electrical(s) == add(electrical(e1), electrical(e2))
        assert el_additive, 'control failed: the electrical flow must be additive'
        row = {'e1': e1, 'e2': e2, 'F(e1)': show(f1), 'F(e2)': show(f2), 'F(e1+e2)': show(fs),
               'F(e1)+F(e2)': show(add(f1, f2)), 'additive': additive, 'electrical_additive': el_additive,
               'steps': [n1, n2, ns]}
        report['pairs'].append(row)
        print(f'e1={e1} e2={e2}: F(e1+e2)={show(fs)} F(e1)+F(e2)={show(add(f1, f2))} additive={additive} '
              f'(electrical additive={el_additive})')
    report['non_additive_pairs'] = sum(1 for r in report['pairs'] if not r['additive'])
    print('non-additive pairs:', report['non_additive_pairs'], 'of', len(pairs))
    with open(args.out, 'w') as handle:
        json.dump(report, handle, indent=1)


if __name__ == '__main__':
    main()
