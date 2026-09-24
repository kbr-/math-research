"""Sequential transfer hypothesis: after quotienting by earlier clauses, is the algebra free over the next clause's forms?

Setting (one board row y plus the bulk, u = 1): P' = assignments (c, y), y <= c, without the slice; clauses t = 1..T,
each forbidding value patterns of its own forms.  G_{t-1} = gr of the functions on P' allowed by clauses 1..t-1 (top
ideal of the point ideal (c^2-c, y^2-y, cy-y, clauses_<t), saturated homogenization at z = 0).
Tested statement (step t of the sequential transfer): G_{t-1} is free through degree D over
F[S, R, W_t]/(p-th powers), acting by s = sum c_j, r = sum y_j and clause t's forms; by graded Nakayama, iff
HF(G_{t-1}/(s, r, l_t)) = [q^k] HS(G_{t-1}) ((1-q)/(1-q^p))^(2 + k_t) for k <= D.
Control ('joint'): freeness of G_0 over all clauses' forms at once, which fails beyond the generic-form threshold.
Families as in closed_row_freeness.py: 'selectors' (one dense form per clause), 'clauses' (two dense forms per clause).
Usage: python3 seq_freeness.py OUT.json N:D:seed:family:T [...]"""
import json, random, subprocess, sys, time
out = sys.argv[1]; res = []; p = 3
for case in sys.argv[2:]:
    N, D, seed, fam, T = case.split(':'); N, D, seed, T = int(N), int(D), int(seed), int(T)
    rnd = random.Random(seed); kf = 1 if fam == 'selectors' else 2
    forms = []
    for _ in range(T):
        fs = []
        while len(fs) < kf:
            f = [rnd.randrange(1, p) for _ in range(N)]
            if len(set(f)) > 1: fs.append(f)
        forms.append((fs, [rnd.randrange(p) for _ in range(kf)]))
    c = lambda j: f'c({j+1})'
    lf = lambda f: '(' + '+'.join(f'{f[j]}*{c(j)}' for j in range(N)) + ')'
    clause = lambda fs, vs: '*'.join(f'(1-({lf(f)}-{v})^{p-1})' for f, v in zip(fs, vs))
    base = [f'{c(j)}^2-{c(j)}' for j in range(N)] + [f'y({j+1})^2-y({j+1})' for j in range(N)] + [f'{c(j)}*y({j+1})-y({j+1})' for j in range(N)]
    s_ = '+'.join(c(j) for j in range(N)); r_ = '+'.join(f'y({j+1})' for j in range(N))
    def hf_pair(prev_clauses, act_forms):
        lines = [f'ring O = {p}, (c(1..{N}), y(1..{N}), z), dp;', 'option(redSB);',
                 'ideal P = ' + ', '.join(base + prev_clauses) + ';', 'ideal H = homog(std(P), z);', 'H = sat(H, z)[1];',
                 'H = subst(H, z, 0);', f'ring Rg = {p}, (c(1..{N}), y(1..{N})), dp;', 'option(redSB);', f'degBound = {D};',
                 'ideal G = std(imap(O, H));', 'ideal K = std(G + ideal(' + ', '.join([s_, r_] + [lf(f) for f in act_forms]) + '));',
                 'string a = "HG {"; string b = "HK {"; int t;',
                 f'for (t = 0; t <= {D}; t++) {{ if (t > 0) {{ a = a + ","; b = b + ","; }} a = a + string(size(kbase(G, t))); b = b + string(size(kbase(K, t))); }}',
                 'print(a + "}"); print(b + "}");', 'quit;']
        path = out.replace('.json', f'_{N}_D{D}_s{seed}_{fam}{T}_{len(prev_clauses)}_{len(act_forms)}.sing'); open(path, 'w').write('\n'.join(lines) + '\n')
        run = subprocess.run(['Singular', '-q', path], capture_output=True, text=True)
        hf = {l.split()[0]: [int(v) for v in l.split(' ', 1)[1].strip('{} ').split(',')] for l in run.stdout.splitlines() if l.startswith(('HG', 'HK'))}
        if 'HG' not in hf: print(run.stdout[-800:], run.stderr[-800:]); raise SystemExit(1)
        return hf['HG'], hf['HK']
    def predict(HG, ngen):
        inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(D + 1)]; cc = [1] + [0] * D
        for _ in range(ngen): cc = [sum(cc[i] * inv[k - i] for i in range(k + 1)) for k in range(D + 1)]
        return [sum(HG[i] * cc[k - i] for i in range(k + 1)) for k in range(D + 1)]
    t0 = time.time(); steps = []
    for t in range(T):
        HG, HK = hf_pair([clause(fs, vs) for fs, vs in forms[:t]], forms[t][0])
        pred = predict(HG, 2 + kf)
        steps.append(dict(step=t + 1, HS_G=HG, HF=HK, predicted=pred, excess=[a - b for a, b in zip(HK, pred)]))
    HG, HK = hf_pair([], [f for fs, _ in forms for f in fs]); pred = predict(HG, 2 + kf * T)
    joint = dict(HF=HK, predicted=pred, excess=[a - b for a, b in zip(HK, pred)])
    row = dict(case=case, steps=steps, joint=joint, seconds=round(time.time() - t0, 1))
    res.append(row); print(json.dumps({'case': case, 'steps': [s['excess'] for s in steps], 'joint': joint['excess'], 'seconds': row['seconds']}), flush=True)
json.dump(res, open(out, 'w'), indent=1)
