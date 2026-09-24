"""Independent check of hereditary_falls.py in Singular.

For a member of hereditary_falls.py (same forms and values from the same seed) and a hole set S, compute
dim ker(z : B_e -> B_{e+1}) for B = F_p[C_rest, z] / J_S, where J_S is the saturated homogenization of the member's
ideal (C_j^2 - C_j, sum C - m, member polynomial) with C_S := z substituted. Quantity: HF_B(e) + HF_A(e+1) -
HF_B(e+1), A = B/zB, from Groebner bases truncated at degree Dmax (exact for homogeneous ideals).
Usage: python3 validate_hereditary.py OUT.json N:p:m:seed:member:S1,S2,..:Dmax [...]"""
import json, random, subprocess, sys
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    N, p, m, seed, member, S, Dmax = case.split(':'); N, p, m, seed, Dmax = int(N), int(p), int(m), int(seed), int(Dmax)
    S = [int(t) for t in S.split(',')]; rnd = random.Random(seed)
    phi = []
    while len(phi) < 2:
        f = [rnd.randrange(1, p) for _ in range(N)]
        if len(set(f)) > 1: phi.append(f)
    v = [rnd.randrange(p) for _ in range(2)]
    c = lambda j: f'c({j+1})'
    ell = lambda b: '(' + '+'.join(f'{phi[b][j]}*{c(j)}' for j in range(N)) + ')'
    ind = lambda b: f'(1-({ell(b)}-{v[b]})^{p-1})'
    h = {'merge': f'{c(0)}*{c(1)}', 'selector': ind(0), 'clause2': f'{ind(0)}*{ind(1)}'}[member]
    gens = [f'{c(j)}^2-{c(j)}' for j in range(N)] + ['+'.join(c(j) for j in range(N)) + f'-{m}', h]
    script = '\n'.join([f'ring O = {p}, (c(1..{N}), z), dp;', 'option(redSB);', 'ideal I = ' + ', '.join(gens) + ';',
        'ideal H = homog(std(I), z);', 'H = sat(H, z)[1];'] + [f'H = subst(H, {c(j)}, z);' for j in S] + [
        f'degBound = {Dmax};', 'ideal GB = std(H);', 'ideal GA = std(H + ideal(z));',
        'string sb = "HFB {"; string sa = "HFA {"; int t;',
        f'for (t = 0; t <= {Dmax}; t++) {{ if (t > 0) {{ sb = sb + ","; sa = sa + ","; }} '
        'ideal gb = GB; ideal ga = GA;',
        # the substituted variables c(j), j in S, are still ring variables: count only monomials free of them
        'sb = sb + string(size(kbase(std(GB + ideal(' + ','.join(c(j) for j in S) + ')), t)));',
        'sa = sa + string(size(kbase(std(GA + ideal(' + ','.join(c(j) for j in S) + ')), t))); }',
        'print(sb + "}"); print(sa + "}");', 'quit;'])
    path = out.replace('.json', f'_{member}_N{N}_s{seed}_S{"-".join(map(str, S))}.sing'); open(path, 'w').write(script + '\n')
    run = subprocess.run(['Singular', '-q', path], capture_output=True, text=True)
    hf = {l.split()[0]: [int(x) for x in l.split(' ', 1)[1].strip('{} ').split(',')]
          for l in run.stdout.splitlines() if l.startswith(('HFB', 'HFA'))}
    if 'HFB' not in hf: print(run.stdout[-1500:], run.stderr[-1500:]); raise SystemExit(1)
    B, A = hf['HFB'], hf['HFA']
    row = dict(case=case, HF_B=B, HF_A=A, ker_z=[B[e] + A[e + 1] - B[e + 1] for e in range(Dmax)])
    res.append(row); print(json.dumps(row), flush=True)
json.dump(res, open(out, 'w'), indent=1)
