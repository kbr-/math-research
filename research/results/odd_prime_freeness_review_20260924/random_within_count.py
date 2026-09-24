"""Route-review falsification test: are random F_3 inventories within the generic-forms count free?

thm:general-forms-freeness gives, for e <= m(floor(N/(2t-1)) - 1), a nonempty Zariski-open set of e-tuples G
over which the weak top algebra A = A~/(row sums) is free through t; by lem:row-sum-absorption that is freeness
of A~ over R + G (R the row sums). It says nothing about a given F_3-rational tuple. This test draws uniformly
random F_3 tuples G at the theorem's largest e and counts how many are free through t (HF(A~/(R,G)) equal to
the prediction through t), and how many violate the line condition (some nonzero direction of R + G meets fewer
than 2t-1 columns), which forces non-freeness. Usage: python3 random_within_count.py OUT.json"""
import itertools, json, sys, time
import numpy as np
sys.path.insert(0, 'research/results/odd_prime_general_forms_20260924')
from forms_freeness import free_through

def row_sums(N, m):
    out = []
    for b in range(m):
        a = np.zeros((N, m), dtype=int); a[:, b] = 1; out.append(a)
    return out

def min_column_count(forms, N):
    """min over nonzero combinations w of #{j : pi_j(w) != 0}."""
    d = len(forms); best = N
    for w in itertools.product(range(3), repeat=d):
        if not any(w): continue
        col = sum(c * f for c, f in zip(w, forms)) % 3
        best = min(best, int(np.count_nonzero(col.any(axis=1))))
    return best

def main():
    out = {'cases': []}; rng = np.random.default_rng(20260925); t0 = time.time()
    for m, N, t, draws in [(3, 6, 2, 40), (4, 6, 2, 40), (2, 9, 2, 40), (3, 9, 2, 30), (2, 10, 3, 30), (3, 10, 3, 20)]:
        e = m * (N // (2 * t - 1) - 1); free = 0; line_bad = 0; bad_but_line_ok = 0
        for _ in range(draws):
            G = [rng.integers(0, 3, (N, m)) for _ in range(e)]
            forms = row_sums(N, m) + G
            ft, hf, P = free_through(N, m, forms, t)
            cmin = min_column_count(forms, N)
            if ft >= t: free += 1
            if cmin < 2 * t - 1: line_bad += 1
            elif ft < t: bad_but_line_ok += 1
        rec = {'m': m, 'N': N, 't': t, 'e': e, 'draws': draws, 'free': free, 'line_condition_fails': line_bad,
               'not_free_with_line_condition': bad_but_line_ok}
        out['cases'].append(rec); print(json.dumps(rec), flush=True)
    out['seconds'] = round(time.time() - t0, 1); json.dump(out, open(sys.argv[1], 'w'), indent=1); print('seconds', out['seconds'])

if __name__ == '__main__':
    main()
