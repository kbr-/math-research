"""Kernel inputs (for direct_sum.cpp) for chains of width-2 budget clauses over F_3 on the occupancy slice.

Tested statement (read from the kernel's output): excess 0 in the one-row closure-gluing test through D-1 for the
closed member of the allowed set of a chain: forms f_0..f_L (independent dense random column forms), clause i
(i = 1..L) allows "f_{i-1} = u_i or f_i = v_i" (forbids f_{i-1} != u_i and f_i != v_i, as its 4 forbidden points).
Inconsistent chain: every link inconsistent, v_i != u_{i+1} (here u_i = 0, v_i = 1); consistent chain: v_i = u_{i+1} = 0.
Usage: python3 chain_inputs.py OUTDIR N:D:m:seed:L:kind [...]   (kind: inc or con); writes OUTDIR/chain_<case>.in"""
import itertools, random, sys
p = 3; outdir = sys.argv[1]
for case in sys.argv[2:]:
    N, D, m, seed, L, kind = case.split(':'); N, D, m, seed, L = int(N), int(D), int(m), int(seed), int(L)
    rnd = random.Random(seed); forms = []
    while len(forms) < L + 1:
        f = [rnd.randrange(1, p) for _ in range(N)]
        if len(set(f)) > 1 and f not in forms: forms.append(f)
    uv = [(0, 1) if kind == 'inc' else (0, 0) for _ in range(L)]
    pts = [(forms[i], forms[i + 1], (uv[i][0] + a) % p, (uv[i][1] + b) % p) for i, a, b in itertools.product(range(L), (1, 2), (1, 2))]
    inp = f'{p} {N} {D} {m} {len(pts)}\n' + ''.join(f'2\n{" ".join(map(str, f))}\n{" ".join(map(str, g))}\n{x} {y}\n' for f, g, x, y in pts) + '-1\n'
    open(f'{outdir}/chain_{case.replace(":", "_")}.in', 'w').write(inp)
