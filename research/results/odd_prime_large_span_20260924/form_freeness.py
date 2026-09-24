"""Is the column tensor power free over its row sums and many random column forms, beyond the seed range?

Tested statement (the hypothesis lem:filtered-freeness-transfer needs in thm:seeded-closure-stability, without seeds):
over F_3, the column tensor power At on R rows and N holes (x_ij^2 = x_ij x_i'j = 0) is free through degree D over
T = F[Y_0..Y_{R-1}, W_1..W_d]/(p-th powers) acting by the row sums r_i and column forms l_b = sum_j phi_b(j) C_j.
By graded Nakayama this holds exactly when HF(At/(r, l)) = [q^k] HS(At)/(1+q+q^2)^(R+d) for k <= D, with the
prediction positive there.  Quantity: excess = HF - prediction in degrees 0..D (Singular Groebner, degBound D).
Families: 'random' (uniform phi in F_3^N), 'coord' (phi_b = indicator of hole b: forms C_b, expected non-free).
Board-seed range for comparison: affine basis multiplicity (p-1)(D+1)^2 at one point.
Usage: python3 form_freeness.py OUT.json R:N:D:d:family:seed [...]"""
import json, random, subprocess, sys, time
from math import comb
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    R, N, D, d, fam, seed = case.split(':'); R, N, D, d, seed = int(R), int(N), int(D), int(d), int(seed); p = 3
    rnd = random.Random(seed)
    x = lambda i, j: f'x({i*N+j+1})'
    C = lambda j: '(' + '+'.join(x(i, j) for i in range(R)) + ')'
    if fam == 'random': phis = [[rnd.randrange(p) for _ in range(N)] for _ in range(d)]
    else: phis = [[1 if j == b else 0 for j in range(N)] for b in range(d)]
    gens = [f'{x(i,j)}^2' for i in range(R) for j in range(N)]
    gens += [f'{x(i,j)}*{x(k,j)}' for j in range(N) for i in range(R) for k in range(i + 1, R)]
    gens += ['+'.join(x(i, j) for j in range(N)) for i in range(R)]
    gens += ['+'.join(f'{f[j]}*{C(j)}' for j in range(N) if f[j]) for f in phis if any(f)]
    script = '\n'.join([f'ring Rg = {p}, (x(1..{R*N})), dp;', 'option(redSB);', f'degBound = {D};',
        'ideal I = ' + ', '.join(gens) + ';', 'ideal G = std(I);', 'string s = "HF {"; int t;',
        f'for (t = 0; t <= {D}; t++) {{ if (t > 0) {{ s = s + ","; }} s = s + string(size(kbase(G, t))); }}',
        'print(s + "}");', 'quit;'])
    path = out.replace('.json', f'_{R}x{N}_D{D}_d{d}_{fam}_s{seed}.sing'); open(path, 'w').write(script + '\n')
    t0 = time.time(); run = subprocess.run(['Singular', '-q', path], capture_output=True, text=True)
    hf = [int(v) for l in run.stdout.splitlines() if l.startswith('HF') for v in l.split(' ', 1)[1].strip('{} ').split(',')]
    if not hf: print(run.stdout[-800:], run.stderr[-800:]); raise SystemExit(1)
    hs = [comb(N, k) * R**k for k in range(D + 1)]   # HS of the column tensor power: (1 + R q)^N
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(D + 1)]; c = [1] + [0] * D
    for _ in range(R + d): c = [sum(c[i] * inv[k - i] for i in range(k + 1)) for k in range(D + 1)]
    pred = [sum(hs[i] * c[k - i] for i in range(k + 1)) for k in range(D + 1)]
    row = dict(case=case, HF=hf, predicted=pred, excess=[a - b for a, b in zip(hf, pred)], prediction_positive=all(v > 0 for v in pred), seconds=round(time.time() - t0, 1))
    res.append(row); print(json.dumps(row), flush=True)
json.dump(res, open(out, 'w'), indent=1)
