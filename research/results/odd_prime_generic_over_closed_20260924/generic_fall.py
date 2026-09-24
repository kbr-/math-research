"""Does a generic member fall over the weak base plus a closed column member (hypothesis (c) over the closed base)?

Tested statement: the homogenized weak unary base (r rows, N holes) plus the closed column member M_D(Z) (all
polynomials of degree <= D vanishing on the column-injective assignments with occupancy in Z), plus one generic selector
1 - (l - v)^2 = 0 with l = sum_ij f_ij x_ij a uniform random row-dependent form, is z-injective below D.
Quantity: dim ker(z: B_k -> B_{k+1}) = HF_B(k) + HF_A(k+1) - HF_B(k+1), A = B/zB, exact Groebner Hilbert functions over
F_3 truncated at D (Singular).  M_D(Z) is the degree <= D part of the saturated homogenization of the radical point ideal
(x^2 - x, column exclusions, h(C)), a Groebner basis homogenized.  Controls: base; base + selector; base + closed member.
Column members: selector forbidding a column form's value (column coefficients in {1,2}); merge C_1 C_2.
Usage: python3 generic_fall.py OUT.json r:N:D:seed:column_member [...]"""
import json, random, subprocess, sys, time
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    r, N, D, seed, cm = case.split(':'); r, N, D, seed = int(r), int(N), int(D), int(seed); rnd = random.Random(seed); p = 3
    x = lambda i, j: f'x({i*N+j+1})'
    C = lambda j: '(' + '+'.join(x(i, j) for i in range(r)) + ')'
    while True:
        phi = [rnd.randrange(1, p) for _ in range(N)]
        if len(set(phi)) > 1: break
    vcol = rnd.randrange(p)
    lcol = '(' + '+'.join(f'{phi[j]}*{C(j)}' for j in range(N)) + ')'
    colmem = {'selector': f'(1-({lcol}-{vcol})^2)', 'merge': f'{C(0)}*{C(1)}'}[cm]
    f = [[rnd.randrange(p) for _ in range(N)] for _ in range(r)]; vg = rnd.randrange(p)
    lgen = '(' + '+'.join(f'{f[i][j]}*{x(i,j)}' for i in range(r) for j in range(N) if f[i][j]) + ')'
    generic = f'(1-({lgen}-{vg})^2)'
    point = [f'{x(i,j)}^2-{x(i,j)}' for i in range(r) for j in range(N)]
    point += [f'{x(i,j)}*{x(k,j)}' for j in range(N) for i in range(r) for k in range(i + 1, r)]
    rows = ['(' + '+'.join(x(i, j) for j in range(N)) + '-z)' for i in range(r)]
    boole_h = [f'{x(i,j)}^2-{x(i,j)}*z' for i in range(r) for j in range(N)] + point[r * N:]
    systems = {'base': ('boole', []), 'base+generic': ('boole', [generic]), 'closed': ('closed', []), 'closed+generic': ('closed', [generic])}
    for label, (kind, extra) in systems.items():
        lines = [f'ring R = {p}, (x(1..{r*N}), z), dp;', 'option(redSB);']
        if kind == 'closed':
            lines += ['ideal P = ' + ', '.join(point + [colmem]) + ';', 'ideal H = homog(std(P), z);',
                      f'ideal HD; int a; for (a = 1; a <= size(H); a++) {{ if (deg(H[a]) <= {D}) {{ HD = HD + H[a]; }} }}',
                      'ideal I = HD, ' + ', '.join(rows) + ';']
        else:
            lines += ['ideal I = ' + ', '.join(boole_h + rows) + ';']
        for e in extra: lines += [f'I = I + homog({e}, z);']
        lines += [f'degBound = {D};', 'ideal GB = std(I);', 'ideal GA = std(I + ideal(z));',
                  'string sb = "HFB {"; string sa = "HFA {"; int t;',
                  f'for (t = 0; t <= {D}; t++) {{ if (t > 0) {{ sb = sb + ","; sa = sa + ","; }} '
                  'sb = sb + string(size(kbase(GB, t))); sa = sa + string(size(kbase(GA, t))); }',
                  'print(sb + "}"); print(sa + "}");', 'quit;']
        path = out.replace('.json', f'_{label}_{r}x{N}_D{D}_s{seed}_{cm}.sing'); open(path, 'w').write('\n'.join(lines) + '\n')
        t0 = time.time(); run = subprocess.run(['Singular', '-q', path], capture_output=True, text=True)
        hf = {l.split()[0]: [int(v) for v in l.split(' ', 1)[1].strip('{} ').split(',')] for l in run.stdout.splitlines() if l.startswith(('HFB', 'HFA'))}
        if 'HFB' not in hf: print(run.stdout[-1500:], run.stderr[-1500:], flush=True); raise SystemExit(1)
        B, A = hf['HFB'], hf['HFA']
        row = dict(case=case, system=label, HF_B=B, HF_A=A, ker_z=[B[k] + A[k + 1] - B[k + 1] for k in range(D)], seconds=round(time.time() - t0, 1))
        res.append(row); print(json.dumps(row), flush=True)
json.dump(res, open(out, 'w'), indent=1)
