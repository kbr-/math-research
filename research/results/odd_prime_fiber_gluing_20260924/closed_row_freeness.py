"""Is the associated graded algebra of functions on a closed column member's assignments row-free (closure gluing)?

Tested statement, one row (u = 1) over F_p: let E = F[c_1..c_N, y_1..y_N]/(c_j^2, y_j^2, c_j y_j) (one board row y
plus the bulk, c_j = C_j), Q-tops G = the top ideal of the member's occupancy system (it contains s = sum_j c_j), and
Abar = E/(G). Condition (ii) for u = 1 says Abar is free over F[rho]/(rho^p), rho = sum_j y_j, in degrees < D, i.e.
(I : rho) = I + (rho^(p-1)) in degrees <= D-1, I = (relations of E) + G. The inclusion "contains" always holds
(rho^p = 0 in E), so the test compares Hilbert functions: excess[k] = HF(I + rho^(p-1))[k] - HF(I : rho)[k] >= 0,
and (ii) holds in degree k exactly when excess[k] = 0.
Members: 'base' (G = (s)), 'onto' (all c_j), 'merge' (s, c_1 c_2), 'linear' (the top ideal of s = m, l = v for
a column form l = sum phi_j C_j), 'e3pin' (e_3(c) fixed mod p, a symmetric count pin of degree 3), 'selectorsT' (T selectors on independent dense forms, span T), 'clausesT' (T clauses, each forbidding one value pattern of two fresh dense random
forms: an entangled family of span 2T), 'pairs' (at most one occupied hole in each pair 2t, 2t+1 of a perfect
matching: span N/2 of forms C_a + C_b), 'selector' (forbid l = v: 1 - (l-v)^(p-1) = 0), 'clause2' (forbid l_1 = v_1 and
l_2 = v_2). Top ideals of the occupancy systems are computed exactly: homogenize the ideal
(C_j^2 - C_j, s - m, member), saturate by z, set z = 0.
CLOSED VERSION: here G is the top ideal of the vanishing ideal of the assignment set P_Z = {(c, y) : c in Z, y <= c}
(c_j = hole j occupied, y_j = occupied by the board row), i.e. of (c_j^2 - c_j, y_j^2 - y_j, c_j y_j - y_j, s - m,
member), computed as its saturated homogenization at z = 0. This is the top algebra of the member closed under all
polynomials vanishing on its allowed assignments (the placed-pigeon closure), which is what closure gluing needs.
Usage: python3 closed_row_freeness.py OUT.json N:D:p:m:seed[:member,member...] [...]"""
import json, random, subprocess, sys, time
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    parts = case.split(':'); N, D, p, m, seed = map(int, parts[:5]); only = parts[5].split(',') if len(parts) > 5 else None
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
               'linear': [f'{ell(0)}-{v[0]}'], 'selector': [ind(0)], 'clause2': [f'{ind(0)}*{ind(1)}'],
               'pairs': [f'{c(2*t)}*{c(2*t+1)}' for t in range(N // 2)]}
    # entangled clause family: T clauses, each forbidding one value pattern of 2 fresh random dense forms (span 2T)
    fam = []
    for _ in range(4):
        fs = []
        while len(fs) < 2:
            f = [rnd.randrange(1, p) for _ in range(N)]
            if len(set(f)) > 1: fs.append(f)
        fam.append((fs, [rnd.randrange(p) for _ in range(2)]))
    lf = lambda f: '(' + '+'.join(f'{f[j]}*{c(j)}' for j in range(N)) + ')'
    clause = lambda fs, vs: '*'.join(f'(1-({lf(f)}-{v})^{p-1})' for f, v in zip(fs, vs))
    import itertools as _it
    e3 = '+'.join(f'{c(a)}*{c(b)}*{c(d)}' for a, b, d in _it.combinations(range(N), 3))
    members['e3pin'] = [f'({e3})-{rnd.randrange(p)}']   # pins e_3(c) mod p (weight mod p^2 by Lucas): degree 3
    for T in (2, 3, 4):
        members[f'clauses{T}'] = [clause(fs, vs) for fs, vs in fam[:T]]
        # T selectors on independent dense forms (degree p-1 each, visible at D >= p-1; span T)
        members[f'selectors{T}'] = [clause(fs[:1], vs[:1]) for fs, vs in fam[:T]]
    for label, mem in members.items():
        if only and label not in only: continue
        occ = [f'{c(j)}^2-{c(j)}' for j in range(N)] + [f'y({j+1})^2-y({j+1})' for j in range(N)]
        occ += [f'{c(j)}*y({j+1})-y({j+1})' for j in range(N)] + [f'{s}-{m}'] + mem
        script = '\n'.join([
            f'ring O = {p}, (c(1..{N}), y(1..{N}), z), dp;', 'option(redSB);',
            'ideal J = ' + ', '.join(occ) + ';', 'ideal Jh = homog(std(J), z);', 'Jh = sat(Jh, z)[1];',
            'Jh = subst(Jh, z, 0);',
            f'ring R = {p}, (c(1..{N}), y(1..{N})), dp;', 'option(redSB);', f'degBound = {D+1};',
            'ideal G = imap(O, Jh);',
            'ideal I = G;',
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
