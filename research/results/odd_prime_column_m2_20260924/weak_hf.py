"""Hilbert functions through degree 3 of quotients of the weak unary PHP top algebra over F_3, computed in Macaulay2.

A = F_3[x_{i,j} : i < n+1 pigeons, j < n holes] / (x_{ij}^2, x_{ij} x_{i'j} (i != i'), sum_j x_{ij}), as in the
component-hypothesis entry; a column-type form is l_phi = sum_{i,j} phi(j) x_{ij}; a random form has uniform coefficients.
For each listed system of forms S, prints HF(A/(S)A, t) for t = 0..3, from the leading terms of a Groebner basis truncated at
degree 3 (exact for t <= 3 since all generators are homogeneous).  Python only writes the .m2 script and parses its output.
Usage: python3 weak_hf.py --n 8 --systems SYSTEMS.json --out OUT.json   (SYSTEMS.json: {name: [form, ...]}, each form an
(n+1) x n coefficient list; the empty system gives HS_A)"""
import json, os, subprocess, sys, time
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); n = int(a['--n']); systems = json.load(open(a['--systems'])); outp = a['--out']
P1 = n + 1
var = lambda i, j: f'x_({i},{j})'
lines = [f'R = ZZ/3[x_(0,0)..x_({P1-1},{n-1})];',
         'base = {' + ', '.join([f'{var(i,j)}^2' for i in range(P1) for j in range(n)]
                               + [f'{var(i,j)}*{var(k,j)}' for j in range(n) for i in range(P1) for k in range(i + 1, P1)]
                               + ['(' + ' + '.join(var(i, j) for j in range(n)) + ')' for i in range(P1)]) + '};']
def form(F): return '(' + ' + '.join(f'{int(F[i][j]) % 3}*{var(i,j)}' for i in range(P1) for j in range(n) if int(F[i][j]) % 3) + ')'
for name, forms in systems.items():
    gens = 'base' + (' | {' + ', '.join(form(F) for F in forms) + '}' if forms else '')
    lines += [f'I = ideal({gens});', 'G = gb(I, DegreeLimit => 3);', 'L = monomialIdeal leadTerm G;',
              f'print("HF {name} " | toString apply(4, t -> hilbertFunction(t, L)));']
lines.append('exit 0')
script = outp.replace('.json', '.m2'); open(script, 'w').write('\n'.join(lines) + '\n')
t0 = time.time(); res = subprocess.run(['M2', '--script', script], capture_output=True, text=True)
out = {}
for line in res.stdout.splitlines():
    if line.startswith('HF '):
        _, name, rest = line.split(' ', 2); out[name] = [int(x) for x in rest.strip('{} ').split(',')]
print(res.stderr[-2000:] if res.returncode else '', flush=True)
print(json.dumps(out), f'({time.time()-t0:.0f}s)', flush=True)
json.dump(dict(n=n, systems=systems, HF=out, seconds=round(time.time() - t0, 1)), open(outp, 'w'), indent=1)
