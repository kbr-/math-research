"""Planted generic selector families over the weak base in range: do satisfiable families fall beyond the Taylor count?

Tested statement (joint-span review, next step): the homogenized weak unary base (r rows, N holes) plus M selectors
1 - (l_t - v_t)^2, l_t = sum_ij f_ij x_ij uniform random row-dependent forms, is z-injective below D:
dim ker(z: B_k -> B_{k+1}) = HF_B(k) + HF_A(k+1) - HF_B(k+1) = 0 for k < D, from exact truncated Groebner Hilbert
functions over F_3 (Singular). Members 'psel<M>': planted values v_t != l_t(x*) for the fixed matching x* (row i in hole i), since
1 - (l - v)^2 = 0 means l != v, so the family is satisfiable with the base; 'gsel<M>': uniform random values (control). The Taylor count at 3x18, D=3 is
about gamma_3/(gamma_1-1) = 18065/50.
Usage: python3 planted_fall.py OUT.json r:N:D:seed:member ...   (member: base, gsel<M>, psel<M>)"""
import json, random, subprocess, sys, time
out = sys.argv[1]; res = []; p = 3
for case in sys.argv[2:]:
    r, N, D, seed, member = case.split(':'); r, N, D, seed = int(r), int(N), int(D), int(seed); rnd = random.Random(seed)
    cells = [(i, j) for i in range(r) for j in range(N)]
    x = lambda i, j: f'x({i*N+j+1})'
    extra = []
    if member[:4] in ('gsel', 'psel'):
        for _ in range(int(member[4:])):
            coef = [rnd.randrange(p) for _ in cells]; v = rnd.randrange(p)
            if member.startswith('psel'):   # planted: 1 - (l - v)^2 = 0 means l != v, so v != l(x*), x_ij = 1 iff j == i
                v = (sum(a for a, (i, j) in zip(coef, cells) if i == j) + rnd.randrange(1, p)) % p
            l = '(' + '+'.join(f'{a}*{x(i, j)}' for a, (i, j) in zip(coef, cells) if a) + ')'
            extra.append(f'(1-({l}-{v})^2)')
    elif member == 'merge':
        C = lambda j: '(' + '+'.join(x(i, j) for i in range(r)) + ')'
        extra.append(f'{C(0)}*{C(1)}')
    gens = [f'{x(i, j)}^2-{x(i, j)}*z' for i, j in cells]
    gens += [f'{x(i, j)}*{x(k, j)}' for (i, j) in cells for k in range(i + 1, r)]
    gens += ['(' + '+'.join(x(i, j) for j in range(N)) + '-z)' for i in range(r)]
    lines = [f'ring R = {p}, (x(1..{r*N}), z), dp;', 'option(redSB);', 'ideal I = ' + ', '.join(gens) + ';']
    lines += [f'I = I + homog({e}, z);' for e in extra]
    lines += [f'degBound = {D};', 'ideal GB = std(I);', 'ideal GA = std(I + ideal(z));',
              'string sb = "HFB {"; string sa = "HFA {"; int t;',
              f'for (t = 0; t <= {D}; t++) {{ if (t > 0) {{ sb = sb + ","; sa = sa + ","; }} '
              'sb = sb + string(size(kbase(GB, t))); sa = sa + string(size(kbase(GA, t))); }',
              'print(sb + "}"); print(sa + "}");', 'quit;']
    path = out.replace('.json', f'_{case.replace(":", "_")}.sing'); open(path, 'w').write('\n'.join(lines) + '\n')
    t0 = time.time(); run = subprocess.run(['Singular', '-q', path], capture_output=True, text=True)
    hf = {l.split()[0]: [int(v) for v in l.split(' ', 1)[1].strip('{} ').split(',')] for l in run.stdout.splitlines() if l.startswith(('HFB', 'HFA'))}
    if 'HFB' not in hf: print(run.stdout[-1500:], run.stderr[-1500:], flush=True); raise SystemExit(1)
    B, A = hf['HFB'], hf['HFA']
    row = dict(case=case, HF_B=B, HF_A=A, ker_z=[B[k] + A[k + 1] - B[k + 1] for k in range(D)], seconds=round(time.time() - t0, 1))
    res.append(row); print(json.dumps(row), flush=True); json.dump(res, open(out, 'w'), indent=1)
