"""In-range closed one-row test (direct-sum kernel direct_sum.cpp) for an inconsistent pair of budget clauses.

Tested statement: excess 0 in the one-row closure-gluing test, ker(rho: G_k -> G_{k+1}) = rho^{p-1} G_{k-p+1} for
k <= D-1, for the closed member of the slice allowed set cut by two width-2 budget clauses over F_3:
  A forbids {l != 0 and a1 != 0},  B forbids {l != c and a2 != 0},
l, a1, a2 independent dense random column forms.  c != 0: the pair is inconsistent (l = 0 and l = c cannot both hold),
non-local at degree 2 (thm:budget-cluster-dichotomy, t = 1); c = 0: consistent control; 'base': no clauses.
Each clause is passed to the kernel as its 4 forbidden points.  Usage: python3 pair_freeness.py BIN OUT.json N:D:m:seed:variant   (BIN = 'emit' writes the kernel input to OUT.in and exits)"""
import itertools, json, random, subprocess, sys, time
p = 3; binp, out = sys.argv[1], sys.argv[2]; res = []
for case in sys.argv[3:]:
    N, D, m, seed, variant = case.split(':'); N, D, m, seed = int(N), int(D), int(m), int(seed)
    rnd = random.Random(seed); forms = []
    while len(forms) < 3:
        f = [rnd.randrange(1, p) for _ in range(N)]
        if len(set(f)) > 1 and f not in forms: forms.append(f)
    l, a1, a2 = forms; clauses = []
    if variant != 'base':
        c = int(variant[1:])
        spec = [(a1, [1, 2]), (a2, [(c + 1) % p, (c + 2) % p])]
        for (g, lvals), u, w in itertools.product(spec, [0, 1], (1, 2)):
            clauses.append(([l, g], [lvals[u], w]))
    inp = f'{p} {N} {D} {m} {len(clauses)}\n' + ''.join(
        f'{len(fs)}\n' + '\n'.join(' '.join(map(str, f)) for f in fs) + '\n' + ' '.join(map(str, vs)) + '\n' for fs, vs in clauses) + '-1\n'
    if binp == 'emit': open(out + '.in', 'w').write(inp); continue
    t0 = time.time(); run = subprocess.run([binp], input=inp, capture_output=True, text=True)
    if run.returncode: print(run.stderr[-800:]); raise SystemExit(1)
    d = json.loads(run.stdout.strip().splitlines()[-1])
    row = dict(case=case, variant=variant, dims=d['dims'], excess=d['excess'], seconds=round(time.time() - t0, 1))
    res.append(row); print(json.dumps(row), flush=True); json.dump(res, open(out, 'w'), indent=1)
