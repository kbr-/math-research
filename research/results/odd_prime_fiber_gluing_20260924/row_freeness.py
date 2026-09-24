"""Is the board modulo a column member's tops free over the row-sum algebra (condition (ii) of fiber gluing)?

Tested statement, one row (u = 1) over F_p: let E = F[c_1..c_N, y_1..y_N]/(c_j^2, y_j^2, c_j y_j) (one board row y
plus the bulk, c_j = C_j), Q-tops G = the top ideal of the member's occupancy system (it contains s = sum_j c_j), and
Abar = E/(G). Condition (ii) for u = 1 says Abar is free over F[rho]/(rho^p), rho = sum_j y_j, in degrees < D, i.e.
(I : rho) = I + (rho^(p-1)) in degrees <= D-1, I = (relations of E) + G. The inclusion "contains" always holds
(rho^p = 0 in E), so the test compares Hilbert functions: excess[k] = HF(I + rho^(p-1))[k] - HF(I : rho)[k] >= 0,
and (ii) holds in degree k exactly when excess[k] = 0.
Members: 'base' (G = (s)), 'onto' (all c_j), 'merge' (s, c_1 c_2), 'linear' (the top ideal of s = m, l = v for
a column form l = sum phi_j C_j), 'selector' (forbid l = v: 1 - (l-v)^(p-1) = 0), 'clause2' (forbid l_1 = v_1 and
l_2 = v_2). Top ideals of the occupancy systems are computed exactly: homogenize the ideal
(C_j^2 - C_j, s - m, member), saturate by z, set z = 0.
Usage: python3 row_freeness.py OUT.json N:D:p:m:seed [...]"""
import json, random, subprocess, sys, time
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    N, D, p, m, seed = map(int, case.split(':'))
    rnd = random.Random(seed)
    phi = []
    while len(phi) < 2:  # forms with nonzero coefficients on every hole, not proportional to s
        f = [rnd.randrange(1, p) for _ in range(N)]
        if len(set(f)) > 1:
            phi.append(f)
    c = lambda j: f'c({j+1})'
    s = '(' + '+'.join(c(j) for j in range(N)) + ')'
    ell = lambda b: '(' + '+'.join(f'{phi[b][j]}*{c(j)}' for j in range(N)) + ')'
    v = [rnd.randrange(p) for _ in range(2)]
    ind = lambda b: f'(1-({ell(b)}-{v[b]})^{p-1})'
    members = {'base': [], 'onto': [f'{c(j)}-1' for j in range(N)], 'merge': [f'{c(0)}*{c(1)}'],
               'linear': [f'{ell(0)}-{v[0]}'], 'selector': [ind(0)], 'clause2': [f'{ind(0)}*{ind(1)}']}
    for label, mem in members.items():
        occ = [f'{c(j)}^2-{c(j)}' for j in range(N)] + [f'{s}-{m}'] + mem
        script = '\n'.join([
            f'ring O = {p}, (c(1..{N}), z), dp;', 'option(redSB);',
            'ideal J = ' + ', '.join(occ) + ';', 'ideal Jh = homog(std(J), z);', 'Jh = sat(Jh, z)[1];',
            'Jh = subst(Jh, z, 0);',
            f'ring R = {p}, (c(1..{N}), y(1..{N})), dp;', 'option(redSB);', f'degBound = {D+1};',
            'ideal G = imap(O, Jh);',
            'ideal I = G, ' + ', '.join([f'{c(j)}^2, y({j+1})^2, {c(j)}*y({j+1})' for j in range(N)]) + ';',
            'I = std(I);', 'poly rho = ' + '+'.join(f'y({j+1})' for j in range(N)) + ';',
            'ideal K = std(quotient(I, rho));', f'ideal F = std(I + ideal(rho^{p-1}));',
            'string sk = "HFK {"; string sf = "HFF {"; int t;',
            f'for (t = 0; t < {D}; t++) {{ if (t > 0) {{ sk = sk + ","; sf = sf + ","; }} '
            'sk = sk + string(size(kbase(K, t))); sf = sf + string(size(kbase(F, t))); }',
            'print(sk + "}"); print(sf + "}");', 'quit;'])
        path = out.replace('.json', f'_{label}_N{N}_D{D}_p{p}_m{m}.sing'); open(path, 'w').write(script + '\n')
        t0 = time.time(); run = subprocess.run(['Singular', '-q', path], capture_output=True, text=True)
        hf = {l.split()[0]: [int(x) for x in l.split(' ', 1)[1].strip('{} ').split(',')]
              for l in run.stdout.splitlines() if l.startswith(('HFK', 'HFF'))}
        if 'HFK' not in hf:
            print(run.stdout[-2000:], run.stderr[-2000:], flush=True); raise SystemExit(1)
        row = dict(case=case, member=label, phi=phi if label in ('linear', 'selector', 'clause2') else None, v=v,
                   HF_quotient=hf['HFK'], HF_frobenius=hf['HFF'],
                   excess=[a - b for a, b in zip(hf['HFF'], hf['HFK'])], seconds=round(time.time() - t0, 1))
        res.append(row); print(json.dumps(row), flush=True)
json.dump(res, open(out, 'w'), indent=1)
