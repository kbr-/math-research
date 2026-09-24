"""Build and exactly verify the characteristic-two Catalan truncation construction (Menezes, arXiv 2609.19009).

Over F_2, with y_i = x_i^2 + x_i and s = k - l:
    g_s = sum over S subset [n] and powers of two a_i (i in S) with sum a_i <= s-1 of
          prod_{i in S} y_i^{a_i} * prod_{j not in S} (x_j + 1),
    P   = y_1^l * g_s.
Predicted: multiplicity >= k at every nonzero point, origin order exactly l, degree
n + 2k - 2 - s_2(k-l-1) when n >= s_2(k-l-1) (at most that for every n).

g_s is expanded coordinate by coordinate: a coordinate outside S contributes x^0 or x^1 at cost 0; a
coordinate in S with power a contributes y^a = x^(2a) + x^a (Frobenius) at cost a.  A dynamic program
over (exponent prefix, cost used) keeps parities, so no term list is enumerated.  Each P is checked by
the compiled kernel's `verify` mode (shift-based Hasse multiplicities, cross-checked by direct
evaluation on small cases); one JSON line is appended per case as it finishes.
Usage: bmd_catalan_construction.py KERNEL OUT_JSONL N_MAX K_MAX
"""
import itertools, json, subprocess, sys, os

def s2(t):
    return bin(t).count('1')

def options(budget):
    """(exponent, cost) pairs for one coordinate, each with multiplicity one over F_2."""
    opts = [(0, 0), (1, 0)]
    a = 1
    while a <= budget:
        opts += [(a, a), (2 * a, a)]
        a *= 2
    return opts

def g(n, s):
    state = {((), 0): 1}
    opts = options(s - 1)
    for _ in range(n):
        new = {}
        for ((prefix, used), _), (e, c) in itertools.product(state.items(), opts):
            if used + c <= s - 1:
                key = (prefix + (e,), used + c)
                new[key] = new.get(key, 0) ^ 1
        state = {k: v for k, v in new.items() if v}
    poly = {}
    for (m, _) in state:
        poly[m] = poly.get(m, 0) ^ 1
    return {m for m, v in poly.items() if v}

def times_y1_power(P, l):
    """Multiply by (x_1^2 + x_1)^l: x_1^(l+b) for bit-submasks b of l (Lucas)."""
    out = {}
    shifts = [l + b for b in range(l + 1) if (b & ~l) == 0]
    for m, t in itertools.product(P, shifts):
        key = (m[0] + t,) + m[1:]
        out[key] = out.get(key, 0) ^ 1
    return {m for m, v in out.items() if v}

def main():
    kernel, out, nmax, kmax = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    path = os.path.join(os.path.dirname(os.path.abspath(out)), 'catalan-poly.txt')
    cases = []
    for k in range(2, kmax + 1):
        cases += [(k, n, l) for n, l in itertools.product(range(max(1, k.bit_length() - 1), nmax + 1), range(k))]
    fails = 0
    with open(out, 'a') as fo:
        for k, n, l in cases:
            P = times_y1_power(g(n, k - l), l)
            with open(path, 'w') as f:
                f.write(''.join(' '.join(map(str, m)) + '\n' for m in sorted(P)))
            r = subprocess.run([kernel, 'verify', str(n), str(k), path], capture_output=True, text=True)
            line = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()
            deg = max(sum(m) for m in P)
            pred = n + 2 * k - 2 - s2(k - l - 1)
            ok = (r.returncode == 0 and f'origin_order={l} ' in line and deg <= pred
                  and (deg == pred or n < s2(k - l - 1)))
            fails += not ok
            fo.write(json.dumps({'n': n, 'k': k, 'l': l, 'degree': deg, 'predicted': pred,
                                 'monomials': len(P), 'verify': line, 'ok': ok}) + '\n')
            fo.flush()
    os.remove(path)
    print(f'{len(cases)} cases checked; failures: {fails}')

if __name__ == '__main__':
    main()
