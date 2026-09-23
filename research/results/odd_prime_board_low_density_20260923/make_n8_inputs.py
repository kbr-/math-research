"""Input files for board_degk (n = 8, degree 6): families of width-two product constraints with random row-function forms.
random2 / random4: M = 2 / 4 uniform forms; pair2: a planted overlapping pair (four forms in a random 3-dimensional span
of row functions, each constraint's forms independent, spanning 3 modulo rows); pair4: the planted pair plus two random
constraints.  Writes the JSON record of the forms (n8_families.json) and board_degk's multi-family input files
(header "n k NF", then for each family "M" and its 2M forms): A = random2 + pair2, B = random4 + pair4, C = pair2 + pair4,
D = random2 + random4.  Usage: --seed --dir"""
import json, os, sys
import numpy as np
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); rng = np.random.default_rng(int(a['--seed'])); D = a['--dir']; n, P = 8, 9
def rank3(M):
    M = np.array(M, dtype=np.int64) % 3; r = 0
    for c in range(M.shape[1]):
        piv = next((i for i in range(r, M.shape[0]) if M[i, c]), None)
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]; M[r] = (M[r] * M[r, c]) % 3
        for i in range(M.shape[0]):
            if i != r and M[i, c]: M[i] = (M[i] - M[i, c] * M[r]) % 3
        r += 1
    return r
mod_rows = lambda F: ((F - F[:, :1]) % 3)[:, 1:].reshape(-1)
rnd = lambda: rng.integers(0, 3, size=(P, n))
def planted_pair():
    while True:
        base = [rnd() for _ in range(3)]
        if rank3([mod_rows(b) for b in base]) < 3: continue
        co = [rng.integers(0, 3, size=3) for _ in range(4)]
        if rank3(co[:2]) == 2 and rank3(co[2:]) == 2 and rank3(co) == 3:
            return [sum(int(c) * b for c, b in zip(cc, base)) % 3 for cc in co]
fams = {'random2': [rnd() for _ in range(4)], 'pair2': planted_pair()}
fams['random4'] = [rnd() for _ in range(8)]; fams['pair4'] = planted_pair() + [rnd() for _ in range(4)]
rec = {}
for name, forms in fams.items():
    rec[name] = dict(M=len(forms) // 2, planted_span_mod_rows=rank3([mod_rows(F) for F in forms[:4]]) if 'pair' in name else None,
                     family_rank_mod_rows=rank3([mod_rows(F) for F in forms]), forms=[F.tolist() for F in forms])
    print(name, rec[name]['M'], rec[name]['planted_span_mod_rows'], rec[name]['family_rank_mod_rows'])
json.dump(rec, open(os.path.join(D, 'n8_families.json'), 'w'), indent=1)
for tag, names in [('A', ['random2', 'pair2']), ('B', ['random4', 'pair4']), ('C', ['pair2', 'pair4']), ('D', ['random2', 'random4'])]:
    with open(os.path.join(D, f'in_n8_k6_{tag}.txt'), 'w') as f:
        f.write(f"{n} 6 {len(names)}\n")
        for nm in names:
            f.write(f"{rec[nm]['M']}\n")
            for F in rec[nm]['forms']:
                for row in F: f.write(' '.join(map(str, row)) + '\n')
