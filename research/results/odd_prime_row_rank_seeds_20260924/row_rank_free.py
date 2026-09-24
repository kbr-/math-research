"""Is the weak unary top algebra free over forms of low affine row rank (the low row-rank seed theorem)?

A = F_3[x_ij]/(x_ij x_i'j (all i, i' incl. i = i'), row sums sum_j x_ij), m rows, N holes.  Forms l_b = sum_ij f^b_ij x_ij.
Tested statement: A is free through degree t over F[W_1..W_d]/(W^3), W_b -> l_b, i.e. (prop:syzygies-as-tor, J = m)
HF(A/(l_1..l_d)A)_k = [q^k] HS_A * ((1-q)/(1-q^3))^d for all k <= t.  Exact Groebner Hilbert functions (Singular).
The theorem predicts freeness when, after a row change, the forms sit on r rows with profile multiplicities
P_0 >= 2r(t+1), each direction profile >= 2(t+1), N >= 2(t+1)(r+t+d); m = r + t rows represent every m.
Cases are given as NAME:m:N:t:spec with spec a ';'-separated list of forms, each a ','-separated list of
row/holeFrom/holeTo/coef blocks (coefficient coef on x_ij for j in [holeFrom, holeTo)), or 'rand' for a uniform
random row-dependent form (seed = NAME's hash-free index).
Usage: python3 row_rank_free.py OUT.json CASE..."""
import json, random, subprocess, sys, time
out = sys.argv[1]; res = []; p = 3
for idx, case in enumerate(sys.argv[2:]):
    name, m, N, t, spec = case.split(':'); m, N, t = int(m), int(N), int(t); rnd = random.Random(1000 + idx)
    x = lambda i, j: f'x({i*N+j+1})'
    forms = []
    for fs in spec.split(';'):
        coef = {}
        if fs == 'rand':
            coef = {(i, j): rnd.randrange(p) for i in range(m) for j in range(N)}
        else:
            for blk in fs.split(','):
                i, a, b, c = map(int, blk.split('/'))
                assert 0 <= i < m and 0 <= a <= b <= N
                for j in range(a, b): coef[(i, j)] = c % p
        forms.append('(' + '+'.join(f'{c}*{x(i, j)}' for (i, j), c in sorted(coef.items()) if c) + ')')
    d = len(forms)
    gens = [f'{x(i, j)}*{x(k, j)}' for i in range(m) for j in range(N) for k in range(i, m)]
    gens += ['(' + '+'.join(x(i, j) for j in range(N)) + ')' for i in range(m)]
    lines = [f'ring R = {p}, (x(1..{m*N})), dp;', 'option(redSB);', 'ideal I = ' + ', '.join(gens) + ';',
             f'degBound = {t};', 'ideal GA = std(I);', 'ideal GL = std(I + ideal(' + ', '.join(forms) + '));',
             'string sa = "HFA {"; string sl = "HFL {"; int k;',
             f'for (k = 0; k <= {t}; k++) {{ if (k > 0) {{ sa = sa + ","; sl = sl + ","; }} '
             'sa = sa + string(size(kbase(GA, k))); sl = sl + string(size(kbase(GL, k))); }',
             'print(sa + "}"); print(sl + "}");', 'quit;']
    path = out.replace('.json', f'_{name}.sing'); open(path, 'w').write('\n'.join(lines) + '\n')
    t0 = time.time(); run = subprocess.run(['Singular', '-q', path], capture_output=True, text=True)
    hf = {l.split()[0]: [int(v) for v in l.split(' ', 1)[1].strip('{} ').split(',')] for l in run.stdout.splitlines() if l.startswith(('HFA', 'HFL'))}
    if 'HFA' not in hf: print(run.stdout[-1500:], run.stderr[-1500:], flush=True); raise SystemExit(1)
    HA, HL = hf['HFA'], hf['HFL']
    ser = [1] + [0] * t                      # ((1-q)/(1-q^3))^d = (1+q+q^2)^(-d)... computed as power series
    inv = [1] + [0] * t                      # 1/(1+q+q^2) = (1-q)/(1-q^3)
    for k in range(1, t + 1): inv[k] = {0: 1, 1: -1, 2: 0}[k % 3]
    for _ in range(d): ser = [sum(ser[a] * inv[k - a] for a in range(k + 1)) for k in range(t + 1)]
    pred = [sum(HA[a] * ser[k - a] for a in range(k + 1)) for k in range(t + 1)]
    row = dict(case=case, d=d, HF_A=HA, HF_quotient=HL, free_prediction=pred, free=HL == pred, seconds=round(time.time() - t0, 1))
    res.append(row); print(json.dumps(row), flush=True); json.dump(res, open(out, 'w'), indent=1)
