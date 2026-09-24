"""Falsification test of conj:effective-board on a three-hole merging member.

Tested statement: the weak unary base on r rows and N columns plus the member {C_1C_2, C_1C_3, C_2C_3}
(at most one of holes 1, 2, 3 occupied; C_j = sum_i x_ij) and its placed-pigeon closure (x_ia C_b and
x_ia x_i'b for distinct holes a, b in {1,2,3}, all rows i, i') has the falls of the weak base on N-2
columns below D.  Quantity: dim ker(z: B_k -> B_{k+1}) from exact Hilbert functions truncated at D (Singular).
Usage: python3 merge3.py OUT.json r:N:D:p [...]"""
import json, subprocess, sys, time
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    r, N, D, p = map(int, case.split(':'))
    x = lambda i, j: f'x({i*N+j+1})'
    C = lambda j: '(' + '+'.join(x(i, j) for i in range(r)) + ')'
    base = [f'{x(i,j)}^2-{x(i,j)}*z' for i in range(r) for j in range(N)]
    base += [f'{x(i,j)}*{x(k,j)}' for j in range(N) for i in range(r) for k in range(i+1, r)]
    base += ['(' + '+'.join(x(i, j) for j in range(N)) + '-z)' for i in range(r)]
    H = [0, 1, 2]
    member = [f'{C(a)}*{C(b)}' for a in H for b in H if a < b]
    closure = member + [f'{x(i,a)}*{C(b)}' for i in range(r) for a in H for b in H if a != b]
    closure += [f'{x(i,a)}*{x(k,b)}' for i in range(r) for k in range(r) for a in H for b in H if a != b]
    gens = base + closure
    script = '\n'.join([f'ring R = {p}, (x(1..{r*N}), z), dp;', 'option(redSB);', f'degBound = {D};',
        'ideal I = ' + ', '.join(gens) + ';', 'ideal GB = std(I);', 'ideal GA = std(I + ideal(z));',
        'string sb = "HFB {"; string sa = "HFA {"; int t;',
        f'for (t = 0; t <= {D}; t++) {{ if (t > 0) {{ sb = sb + ","; sa = sa + ","; }} '
        'sb = sb + string(size(kbase(GB, t))); sa = sa + string(size(kbase(GA, t))); }',
        'print(sb + "}"); print(sa + "}");', 'quit;'])
    path = out.replace('.json', f'_{r}x{N}_D{D}.sing'); open(path, 'w').write(script + '\n')
    t0 = time.time(); run = subprocess.run(['Singular', '-q', path], capture_output=True, text=True)
    hf = {l.split()[0]: [int(v) for v in l.split(' ', 1)[1].strip('{} ').split(',')] for l in run.stdout.splitlines() if l.startswith(('HFB', 'HFA'))}
    B, A = hf['HFB'], hf['HFA']
    row = dict(case=case, system='base+merge3-closure', ker_z=[B[k] + A[k+1] - B[k+1] for k in range(D)], HF_B=B, HF_A=A, seconds=round(time.time()-t0, 1))
    res.append(row); print(json.dumps(row), flush=True)
json.dump(res, open(out, 'w'), indent=1)
