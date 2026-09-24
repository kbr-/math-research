"""Independent check of closed_split.py's closure rows: for the merge member (holes 1, 2 not both occupied) the closed
member's top algebra must be the fat board's (cor:merging-members): generators x_ij^2, x_ij x_i'j, x_i1 x_i'2 (all rows
i, i'), row sums, over F_3, n holes and n + 1 rows.  Prints its Hilbert function through degree 3 (Singular), to compare
with closed_split.py's H of A# for member 'merge'.  Usage: python3 validate_fat.py OUT.json N [...]"""
import json, subprocess, sys
out = sys.argv[1]; res = []
for N in map(int, sys.argv[2:]):
    P1 = N + 1; x = lambda i, j: f'x({i*N+j+1})'
    gens = [f'{x(i,j)}^2' for i in range(P1) for j in range(N)]
    gens += [f'{x(i,j)}*{x(k,j)}' for j in range(N) for i in range(P1) for k in range(i + 1, P1)]
    gens += [f'{x(i,0)}*{x(k,1)}' for i in range(P1) for k in range(P1)]
    gens += ['+'.join(x(i, j) for j in range(N)) for i in range(P1)]
    script = '\n'.join([f'ring R = 3, (x(1..{P1*N})), dp;', 'option(redSB);', 'degBound = 3;', 'ideal I = ' + ', '.join(gens) + ';',
        'ideal G = std(I);', 'string s = "HF {"; int t;', 'for (t = 0; t <= 3; t++) { if (t > 0) { s = s + ","; } s = s + string(size(kbase(G, t))); }',
        'print(s + "}");', 'quit;'])
    path = out.replace('.json', f'_n{N}.sing'); open(path, 'w').write(script + '\n')
    run = subprocess.run(['Singular', '-q', path], capture_output=True, text=True)
    hf = [int(v) for l in run.stdout.splitlines() if l.startswith('HF') for v in l.split(' ', 1)[1].strip('{} ').split(',')]
    res.append(dict(N=N, HF=hf)); print(res[-1], flush=True)
json.dump(res, open(out, 'w'), indent=1)
