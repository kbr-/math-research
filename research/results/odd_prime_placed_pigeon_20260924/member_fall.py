"""Does a column member with no fall in the occupancy ring fall on the weak board?

Tested statement: the homogenized weak unary base on r rows and N columns plus the homogenized column
constraints h(C), C_j = sum_i x_ij, is z-injective below D (hypothesis (c) of relative gluing for that member).
Member tested: {C_1 C_2} (holes 1 and 2 not both occupied), whose occupancy system has no fall.
Quantity: dim ker(z: B_k -> B_{k+1}) = HF_B(k) + HF_A(k+1) - HF_B(k+1), from Groebner leading terms truncated at D
(exact since all generators are homogeneous), in Singular.  Control: the same board without the member. Also tested: the member with its placed-pigeon closure added.
Usage: python3 member_fall.py OUT.json r:N:D:p [...]"""
import json, subprocess, sys, time
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    r, N, D, p = map(int, case.split(':'))
    x = lambda i, j: f'x({i*N+j+1})'
    base = [f'{x(i,j)}^2-{x(i,j)}*z' for i in range(r) for j in range(N)]
    base += [f'{x(i,j)}*{x(k,j)}' for j in range(N) for i in range(r) for k in range(i+1, r)]
    base += ['(' + '+'.join(x(i, j) for j in range(N)) + '-z)' for i in range(r)]
    C = lambda j: '(' + '+'.join(x(i, j) for i in range(r)) + ')'
    member = [f'{C(0)}*{C(1)}']
    # placed-pigeon closure of {C_1 C_2}: pigeon i in hole 1 => hole 2 empty (x_i1 C_2), symmetrically, and no
    # pigeons in both holes (x_i1 x_i'2 for all rows i, i').
    closure = member + [f'{x(i,0)}*{C(1)}' for i in range(r)] + [f'{x(i,1)}*{C(0)}' for i in range(r)]
    closure += [f'{x(i,0)}*{x(k,1)}' for i in range(r) for k in range(r)]
    for label, gens in (('base', base), ('base+member', base + member), ('base+closure', base + closure)):
        script = '\n'.join([f'ring R = {p}, (x(1..{r*N}), z), dp;', 'option(redSB);', f'degBound = {D};',
            'ideal I = ' + ', '.join(gens) + ';', 'ideal GB = std(I);', 'ideal GA = std(I + ideal(z));',
            'string sb = "HFB {"; string sa = "HFA {"; int t;',
            f'for (t = 0; t <= {D}; t++) {{ if (t > 0) {{ sb = sb + ","; sa = sa + ","; }} '
            'sb = sb + string(size(kbase(GB, t))); sa = sa + string(size(kbase(GA, t))); }',
            'print(sb + "}"); print(sa + "}");', 'quit;'])
        path = out.replace('.json', f'_{label}_{r}x{N}_D{D}.sing'); open(path, 'w').write(script + '\n')
        t0 = time.time(); run = subprocess.run(['Singular', '-q', path], capture_output=True, text=True)
        hf = {l.split()[0]: [int(v) for v in l.split(' ', 1)[1].strip('{} ').split(',')] for l in run.stdout.splitlines() if l.startswith(('HFB', 'HFA'))}
        B, A = hf['HFB'], hf['HFA']
        row = dict(case=case, system=label, HF_B=B, HF_A=A, ker_z=[B[k] + A[k+1] - B[k+1] for k in range(D)], seconds=round(time.time()-t0, 1))
        res.append(row); print(json.dumps(row), flush=True)
json.dump(res, open(out, 'w'), indent=1)
