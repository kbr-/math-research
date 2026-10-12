"""Controls for degree_series.py that its reviewer found missing, and the coincidence-free systems.

A coincidence is a (k+1)-set of variables lying in the scopes of a row of label zero and a row of label one.
prop:majority-coincidence-floor: without one, no refutation of degree k + 1 exists.

Part one, the 24 recorded instances, redrawn from their seeds: the number of coincident sets of each.
Refuted by: an instance of exact degree k + 1 with no coincident set, which would contradict the proposition.
Possible because: the count is a comparison of scopes and the degree an elimination; a fault in either shows here.

Part two, a satisfiable system (the first satisfiable draw at w = 5, n = 14): the kernel must find no refutation.
Refuted by: a degree returned for a satisfiable system at any D through the bound given.
Possible because: a wrong generator for a row of either label lies outside the ideal and can produce 1.

Part three, systems drawn until they have no coincidence, use every variable and are unsatisfiable, w = 5:
the exact degree through DMAX, with the kernel's own peak memory read by /usr/bin/time.
Refuted by: a degree of k + 1 = 3 on a system without coincidences, against the proposition.
Possible because: the kernel computes the closure with no knowledge of the scopes' intersections.
No expectation is written for whether the degree is 4 or more than 4: degree 4 would mean a second local
configuration refutes these systems too; more than 4 would support reading the floor at k + 1 as the
coincidences' doing.  The memory estimate, a peak within twice M^2/8 plus 64 MB at the last D computed:
Refuted by: a peak read by /usr/bin/time above that at any case of part three.
Possible because: the kernel keeps a hash index and row copies that the estimate omits.

Usage: controls.py KERNEL SCRATCH_DIR OUT.json SIZING.jsonl N:DMAX ...
"""
import itertools
import json
import math
import random
import re
import subprocess
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
import degree_series as ds


def coincidences(rows, k):
    zero = {t for scope, label in rows if label == 0 for t in itertools.combinations(scope, k + 1)}
    one = {t for scope, label in rows if label == 1 for t in itertools.combinations(scope, k + 1)}
    return len(zero & one)


def timed_degree(kernel, scratch, n, polys, dmax, tag):
    path = f'{scratch}/control_{tag}.txt'
    with open(path, 'w') as handle:
        handle.write(f'{n} {len(polys)}\n' + ''.join(f'{len(p)} ' + ' '.join(map(str, p)) + '\n' for p in polys))
    done = subprocess.run(['/usr/bin/time', '-v', kernel, path, str(dmax)], check=True, capture_output=True, text=True)
    got = json.loads(done.stdout)
    peak = int(re.search(r'Maximum resident set size \(kbytes\): (\d+)', done.stderr).group(1)) * 1024
    return got['degree'], got['dimensions'], peak


def main(kernel, scratch, out, sizing, cases):
    report = {'recorded': [], 'satisfiable': None, 'coincidence_free': []}
    for line in open(sizing):
        row = json.loads(line)
        rows, draws = ds.instance(row['n'], row['w'], row['seed'])
        assert draws == row['draws']
        count = coincidences(rows, row['w'] // 2)
        report['recorded'].append({'w': row['w'], 'n': row['n'], 'seed': row['seed'], 'degree': row['exact_degree'],
                                   'coincident_sets': count, 'consistent_with_floor': count > 0})
    rng = random.Random(4242)
    while True:
        rows = ds.draw(14, 5, rng)
        if ds.satisfiable(14, rows, 2):
            break
    degree, _, _ = timed_degree(kernel, scratch, 14, ds.polynomials(rows, 2), 7, 'satisfiable')
    report['satisfiable'] = {'w': 5, 'n': 14, 'searched_through': 7, 'degree': degree, 'no_refutation': degree is None}
    for n, dmax in cases:
        for seed in (1, 2, 3):
            rng = random.Random(900000 + 1000 * n + seed)
            for draws in itertools.count(1):
                rows = ds.draw(n, 5, rng)
                if coincidences(rows, 2) == 0 and len({i for s, _ in rows for i in s}) == n \
                        and not ds.satisfiable(n, rows, 2):
                    break
            degree, dims, peak = timed_degree(kernel, scratch, n, ds.polynomials(rows, 2), dmax, f'free_{n}_{seed}')
            last = dmax if degree is None else degree
            estimate = sum(math.comb(n, j) for j in range(last + 1)) ** 2 // 8
            result = {'w': 5, 'n': n, 'seed': seed, 'draws': draws, 'searched_through': dmax, 'degree': degree,
                      'closure_dimensions': dims, 'above_floor': degree is None or degree >= 4,
                      'peak_bytes': peak, 'estimate_bytes': estimate,
                      'memory_within_estimate': peak <= 2 * estimate + 64 * 2 ** 20}
            report['coincidence_free'].append(result)
            print(json.dumps(result), flush=True)
    with open(out, 'w') as handle:
        json.dump(report, handle, indent=1)
    recorded = report['recorded']
    print(json.dumps({'recorded': len(recorded), 'all_have_a_coincidence': all(r['consistent_with_floor'] for r in recorded),
                      'coincident_sets_range': [min(r['coincident_sets'] for r in recorded),
                                                max(r['coincident_sets'] for r in recorded)],
                      'satisfiable': report['satisfiable']}))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
         [tuple(map(int, case.split(':'))) for case in sys.argv[5:]])
