"""Is z injective on the homogenized unary PHP base below degree D?  Exact, over F_p, in Macaulay2.

Tested statement (hypothesis (a) of the relative gluing theorem for the base alone): with
B = F_p[x_ij, z]/(homogenized base generators) and A = B/zB, z: B_k -> B_{k+1} is injective for every k < D,
equivalently HF_B(k+1) = HF_B(k) + HF_A(k+1) for k < D (from 0 -> ker -> B_k -> B_{k+1} -> A_{k+1} -> 0).
Bases on r rows and N columns:
  weak:       x_ij^2 - x_ij z,  x_ij x_i'j (i != i'),  sum_j x_ij - z
  functional: the weak generators and x_ij x_ij' (j != j').
Hilbert functions through degree D come from the leading terms of a Groebner basis truncated at degree D, which is
exact there since every generator is homogeneous.  By the row-reduction lemma of the entry, the weak base on any
number of rows is z-injective in degree k when the weak base on k+1 rows is, so r = D rows decides every k < D.
Usage: python3 base_injectivity.py --out OUT.json [--engine singular] CASE [CASE ...]   with CASE = base:r:N:D:p,
e.g. weak:4:7:4:3.  Macaulay2 is the default engine; Singular (degBound, kbase counts) serves the cases where
Macaulay2's garbage collector fails.  Python only writes the script and parses its output."""
import json, subprocess, sys, time

def script(base, r, N, D, p):
    v = lambda i, j: f'x_({i},{j})'
    gens = [f'{v(i,j)}^2 - {v(i,j)}*z' for i in range(r) for j in range(N)]
    gens += [f'{v(i,j)}*{v(k,j)}' for j in range(N) for i in range(r) for k in range(i + 1, r)]
    if base == 'functional':
        gens += [f'{v(i,j)}*{v(i,l)}' for i in range(r) for j in range(N) for l in range(j + 1, N)]
    gens += ['(' + ' + '.join(v(i, j) for j in range(N)) + ' - z)' for i in range(r)]
    if ENGINE == 'singular':
        names = {f'x_({i},{j})': f'x({i*N+j+1})' for i in range(r) for j in range(N)}
        def conv(g):
            for a in sorted(names, key=len, reverse=True):
                g = g.replace(a, names[a])
            return g
        return '\n'.join([
            f'ring R = {p}, (x(1..{r*N}), z), dp;', 'option(redSB);', f'degBound = {D};',
            'ideal I = ' + ', '.join(conv(g) for g in gens) + ';',
            'ideal GB = std(I);', 'ideal GA = std(I + ideal(z));',
            'string sb = "HFB {"; string sa = "HFA {"; int t;',
            f'for (t = 0; t <= {D}; t++) {{ if (t > 0) {{ sb = sb + ","; sa = sa + ","; }} '
            'sb = sb + string(size(kbase(GB, t))); sa = sa + string(size(kbase(GA, t))); }',
            'print(sb + "}"); print(sa + "}");', 'quit;'])
    return '\n'.join([
        f'R = ZZ/{p}[x_(0,0)..x_({r-1},{N-1}), z];',
        'I = ideal(' + ', '.join(gens) + ');',
        f'LB = monomialIdeal leadTerm gb(I, DegreeLimit => {D});',
        f'LA = monomialIdeal leadTerm gb(I + ideal(z), DegreeLimit => {D});',
        f'print("HFB " | toString apply({D+1}, t -> hilbertFunction(t, LB)));',
        f'print("HFA " | toString apply({D+1}, t -> hilbertFunction(t, LA)));',
        'exit 0'])

args = sys.argv[1:]; ENGINE = args[args.index('--engine') + 1] if '--engine' in args else 'm2'
out_path = args[args.index('--out') + 1]; cases = [c for c in args if c.count(':') == 4]
results = []
for case in cases:
    base, r, N, D, p = case.split(':'); r, N, D, p = int(r), int(N), int(D), int(p)
    assert base in ('weak', 'functional') and r >= 1 and N >= 1 and D >= 1
    ext = '.sing' if ENGINE == 'singular' else '.m2'
    path = out_path.replace('.json', f'_{base}_{r}x{N}_D{D}_p{p}{ext}'); open(path, 'w').write(script(base, r, N, D, p) + '\n')
    cmd = ['Singular', '-q', path] if ENGINE == 'singular' else ['M2', '--script', path]
    t0 = time.time(); res = subprocess.run(cmd, capture_output=True, text=True)
    hf = {l.split()[0]: [int(x) for x in l.split(' ', 1)[1].strip('{} ').split(',')] for l in res.stdout.splitlines()
          if l.startswith(('HFB ', 'HFA '))}
    if res.returncode or set(hf) != {'HFB', 'HFA'}:
        print(case, 'FAILED', res.stderr[-1500:], flush=True); sys.exit(1)
    B, A = hf['HFB'], hf['HFA']
    kernel = [B[k] + A[k + 1] - B[k + 1] for k in range(D)]   # dim ker(z: B_k -> B_{k+1})
    row = dict(case=case, engine=ENGINE, base=base, rows=r, N=N, D=D, p=p, HF_B=B, HF_A=A, ker_z=kernel,
               injective_below_D=all(x == 0 for x in kernel), in_range=N >= 2 * D - 1, seconds=round(time.time() - t0, 1))
    results.append(row); print(json.dumps(row), flush=True)
    json.dump(results, open(out_path, 'w'), indent=1)
