"""Driver for direct_sum (compiled): builds the members of closed_row_freeness.py with the same random sequence and
runs the one-row closed test on the direct-sum form.  Usage: python3 run_direct_sum.py BIN OUT.json N:D:p:m:seed:member [...]
Members: base, selector, clause2, selectorsT, clausesT (T = 2,3,4), e3pin, and selT (T = 1..16 further dense selectors; the first 8 as before)."""
import json, random, subprocess, sys, time
binp, out = sys.argv[1], sys.argv[2]; res = []
for case in sys.argv[3:]:
    N, D, p, m, seed, member = case.split(':'); N, D, p, m, seed = int(N), int(D), int(p), int(m), int(seed)
    rnd = random.Random(seed); phi = []
    while len(phi) < 2:
        f = [rnd.randrange(1, p) for _ in range(N)]
        if len(set(f)) > 1: phi.append(f)
    v = [rnd.randrange(p) for _ in range(2)]
    fam = []
    for _ in range(4):
        fs = []
        while len(fs) < 2:
            f = [rnd.randrange(1, p) for _ in range(N)]
            if len(set(f)) > 1: fs.append(f)
        fam.append((fs, [rnd.randrange(p) for _ in range(2)]))
    e3 = rnd.randrange(p)   # drawn after fam, as in closed_row_freeness.py
    more = []                # further dense forms for 'selT' (T up to 16), drawn after the recorded sequence
    for _ in range(16):
        while True:
            f = [rnd.randrange(1, p) for _ in range(N)]
            if len(set(f)) > 1: break
        more.append((f, rnd.randrange(p)))
    clauses, pin = [], -1
    if member == 'selector': clauses = [([phi[0]], [v[0]])]
    elif member == 'clause2': clauses = [(phi, v)]
    elif member.startswith('selectors'): clauses = [([fs[0]], [vs[0]]) for fs, vs in fam[:int(member[9:])]]
    elif member.startswith('clauses'): clauses = [(fs, vs) for fs, vs in fam[:int(member[7:])]]
    elif member == 'e3pin': pin = e3
    elif member.startswith('sel') and member[3:].isdigit(): clauses = [([f], [vv]) for f, vv in more[:int(member[3:])]]
    elif member != 'base': raise SystemExit('unknown member ' + member)
    inp = f'{p} {N} {D} {m} {len(clauses)}\n'
    for fs, vs in clauses:
        inp += f'{len(fs)}\n' + '\n'.join(' '.join(map(str, f)) for f in fs) + '\n' + ' '.join(map(str, vs)) + '\n'
    inp += f'{pin}\n'
    t0 = time.time(); run = subprocess.run([binp], input=inp, capture_output=True, text=True)
    if run.returncode: print(run.stderr[-800:]); raise SystemExit(1)
    d = json.loads(run.stdout.strip().splitlines()[-1])
    row = dict(case=case, member=member, dims=d['dims'], excess=d['excess'], seconds=round(time.time() - t0, 1))
    res.append(row); print(json.dumps(row), flush=True)
    json.dump(res, open(out, 'w'), indent=1)   # saved after every case
