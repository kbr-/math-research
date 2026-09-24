"""Validate the y-coefficient degree formula against the jet kernel on random jets.

Statement tested: for a jet v (|beta| < k) and w(y) = v(x(y_1),...,x(y_n)) with x(Y) = sum_t Y^(2^t),
deg P(v) = max{|eps| + 2|e| : |e| < k, [y^e]( w * prod_{i: eps_i = 0} (1 + x(y_i)) ) != 0}.
The kernel bmd_jet_orders --jet computes deg P(v) from the one-variable y-basis tables.
Usage: bmd_ycoef_check.py BIN OUTDIR TRIALS
"""
import json, random, subprocess, sys
from pathlib import Path


def monos(n, maxdeg):
    if n == 0:
        return [()]
    return [(a,) + m for a in range(maxdeg + 1) for m in monos(n - 1, maxdeg - a)]


def mul(p, q, k):
    r = {}
    for a in p:
        for b in q:
            m = tuple(x + y for x, y in zip(a, b))
            if sum(m) < k:
                r[m] = r.get(m, 0) ^ 1
    return {m for m, c in r.items() if c}


def xseries(n, i, k):
    """x(y_i) truncated below total degree k, as a set of exponent tuples."""
    out, t = set(), 1
    while t < k:
        out.add(tuple(t if j == i else 0 for j in range(n)))
        t *= 2
    return out


def formula_degree(n, k, jet):
    one = {tuple([0] * n)}
    xs = [xseries(n, i, k) for i in range(n)]
    w = set()
    for beta in jet:
        term = set(one)
        for i in range(n):
            for _ in range(beta[i]):
                term = mul(term, xs[i], k)
        w ^= term
    best = -1
    for eps in range(2 ** n):
        f = set(w)
        for i in range(n):
            if not (eps >> i) & 1:
                f = mul(f, one | xs[i], k)
        if f:
            best = max(best, bin(eps).count('1') + 2 * max(sum(m) for m in f))
    return best


def main():
    binary, outdir, trials = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3])
    outdir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20260925)
    cases = [(n, k) for n in (1, 2, 3) for k in range(1, 9)]
    bad = 0
    for t in range(trials):
        n, k = cases[t % len(cases)]
        jet = [m for m in monos(n, k - 1) if rng.random() < 0.3] or [tuple([0] * n)]
        jf = outdir / 'jet.txt'
        jf.write_text(''.join(' '.join(map(str, m)) + '\n' for m in jet))
        got = json.loads(subprocess.run([binary, str(n), str(k), '--jet', str(jf)], check=True,
                                        capture_output=True, text=True).stdout)['degree']
        want = formula_degree(n, k, jet)
        bad += got != want
    print(f'trials {trials} over (n,k) in n<=3, k<=8: mismatches {bad}')


if __name__ == '__main__':
    main()
