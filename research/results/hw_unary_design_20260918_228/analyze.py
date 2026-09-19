#!/usr/bin/env python3
"""Degree-fall analysis of the exact NS runs (cycle 228).

For a board, form type and seed, the clauses are the same in the runs at every degree (same generator
state). G_e(b) = I_e + sum over the first b clauses of Q P_{<=e-h}. A run at degree B reports the pivots
by leading degree, whose partial sum through e is dim(G_B(b) cap P_{<=e}); the run at degree e reports
dim G_e(b) (for e < h, G_e = I_e, read from the base histogram). "No degree fall through b clauses" means
equality for every e < B. Also prints the increments, the clause at which 1 enters, and the first clause
at which the count dim G_B - dim G_{B-1} > m_B forces a fall (Observation F (a))."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
def load(path):
    base = None; hist = {}; cl = {}; mons = None
    for l in open(path):
        if not l.startswith('{'): continue
        r = json.loads(l)
        if 'rank_I' in r: base = r
        elif 'base_pivots_by_leading_degree' in r: hist[0] = r['base_pivots_by_leading_degree']; mons = r['monomials_by_degree']
        elif 'pivots_by_leading_degree' in r and 'clause' in r: hist[r['clause']] = r['pivots_by_leading_degree']
        elif 'terms' in r: cl[r['clause']] = r
    return base, hist, cl, mons
FAMILIES = [(6, 2, '', 3), (7, 2, '', 4), (7, 3, '', 4), (8, 2, '', 3), (8, 2, '_label', 3), (8, 1, '_label', 2), (8, 1, '_label', 3)]
for N, h, tag, B in FAMILIES:
    for seed in (1, 2, 3):
        runs = {}
        for e in range(1, B + 1):
            p = f'{D}/ns_l{N}_d{e}_h{h}{tag}_seed{seed}.jsonl'
            if os.path.exists(p) and os.path.getsize(p): runs[e] = load(p)
        if B not in runs: continue
        base, hist, cl, mons = runs[B]
        incs = [cl[b]['increment'] for b in sorted(cl)]
        tip = next((b for b in sorted(cl) if cl[b]['one_in_span']), None)
        print(f'N={N} h={h}{tag} seed={seed} degree {B}: quotient {base["quotient_dim"]}, clauses run {len(cl)}, 1 enters at {tip}',
              f'(quotient left {cl[tip]["quotient_left"]})' if tip else '')
        print('  increments:', incs[:6], '...', incs[-3:])
        first_fall = None; unchecked = set()
        for b in sorted(hist):
            for e in range(1, B):
                if e < h: dim_e = sum(hist[0][:e + 1])
                elif e in runs and (b == 0 or b in runs[e][2]): dim_e = runs[e][0]['rank_I'] + (runs[e][2][b]['dim_V_mod_I'] if b else 0)
                else: unchecked.add(e); continue
                cap = sum(hist[b][:e + 1])
                if cap != dim_e and first_fall is None: first_fall = (b, e, cap, dim_e, cap - dim_e)
        print('  first degree fall (clause, level e, dim of G_B cap P_<=e, dim G_e, amount):', first_fall,
              f' [levels without a companion run: {sorted(unchecked)}]' if unchecked else '')
        if first_fall:
            b0 = first_fall[0]
            print('  top-degree pivots near the first fall:', [(b, hist[b][B]) for b in sorted(hist) if b0 - 2 <= b <= b0 + 3], ' last:', hist[max(hist)])
        if B - 1 in runs or B - 1 < h:
            forced = None
            for b in sorted(cl):
                if B - 1 < h: low = sum(hist[0][:B])
                elif b in runs[B - 1][2]: low = runs[B - 1][0]['rank_I'] + runs[B - 1][2][b]['dim_V_mod_I']
                else: continue
                if base['rank_I'] + cl[b]['dim_V_mod_I'] - low > mons[B]: forced = b; break
            print(f'  top-degree monomials {mons[B]}; count (a) forces a fall from clause', forced)
