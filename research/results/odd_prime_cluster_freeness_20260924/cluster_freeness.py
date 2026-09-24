"""Closed one-row row-freeness test (direct-sum kernel, direct_sum.cpp) for an inconsistent three-clause cluster.

Tested statement: ker(rho: G_k -> G_{k+1}) = rho^{p-1} G_{k-p+1} for k <= D-1 (the one-row closure-gluing hypothesis,
excess 0) for the closed member of the allowed set Z cut from the occupancy slice (popcount = m mod 3) by three
budget-type clauses of width 2 over F_3 (each forbids "both of its forms nonzero"):
  A: l1 != 0 and a1 != 0;  B: l2 != 0 and a2 != 0;  C: (l1 + l2) - c != 0 and a3 != 0,
with l1, l2, a1, a2, a3 independent dense random column forms (coefficients in {1,2}).
c != 0 is the inconsistent cluster (non-local at degree 6 in form space by prop:member-inconsistency);
c = 0 the consistent control; 'base' has no clauses.  Each clause is passed to the kernel as its 4 forbidden points.
Usage: python3 cluster_freeness.py BIN OUT.json N:D:m:seed:variant [...]   (variant: base, c0, c1, c2)"""
import json, random, subprocess, sys, time
p = 3; binp, out = sys.argv[1], sys.argv[2]; res = []
for case in sys.argv[3:]:
    N, D, m, seed, variant = case.split(':'); N, D, m, seed = int(N), int(D), int(m), int(seed)
    rnd = random.Random(seed); forms = []
    while len(forms) < 5:
        f = [rnd.randrange(1, p) for _ in range(N)]
        if len(set(f)) > 1 and f not in forms: forms.append(f)
    l1, l2, a1, a2, a3 = forms; l12 = [(x + y) % p for x, y in zip(l1, l2)]
    clauses = []
    if variant != 'base':
        c = int(variant[1:])
        for (f, g, bad_f) in [(l1, a1, [1, 2]), (l2, a2, [1, 2]), (l12, a3, [(c + 1) % p, (c + 2) % p])]:
            for u in bad_f:
                for w in (1, 2): clauses.append(([f, g], [u, w]))
    inp = f'{p} {N} {D} {m} {len(clauses)}\n'
    for fs, vs in clauses:
        inp += f'{len(fs)}\n' + '\n'.join(' '.join(map(str, f)) for f in fs) + '\n' + ' '.join(map(str, vs)) + '\n'
    inp += '-1\n'
    t0 = time.time(); run = subprocess.run([binp], input=inp, capture_output=True, text=True)
    if run.returncode: print(run.stderr[-800:]); raise SystemExit(1)
    d = json.loads(run.stdout.strip().splitlines()[-1])
    row = dict(case=case, variant=variant, dims=d['dims'], excess=d['excess'], seconds=round(time.time() - t0, 1))
    res.append(row); print(json.dumps(row), flush=True); json.dump(res, open(out, 'w'), indent=1)
