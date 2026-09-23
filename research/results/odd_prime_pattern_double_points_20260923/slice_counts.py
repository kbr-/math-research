"""Checks the counting formulas of the pattern row reduction against enumeration of the pattern algebra P(R, L):
T(L) = L(L-1)(L-2) - 3(L-2) - 4 label triples per row triple; gamma_3 = C(R,3) T(L); slice dimensions
d_c = #{2-faces f of P(R-1,L) with f + (last,c) a face}: d_0 = d_c (c>=4) = C(R-1,2)((L-1)(L-2)-1), d_1 = C(R-1,2)(L-2)(L-3),
d_2 = C(R-1,2)((L-1)(L-2)-2), d_3 = C(R-1,2)((L-1)(L-2)-3); and ceil(capacity) <= d_1 = min_c d_c."""
import itertools, json, math, sys
PAT3 = {(0, 2, 3), (1, 0, 2), (1, 2, 0), (1, 2, 3)}
ok = lambda labs: not any(labs[i] == 0 and labs[j] == 1 for i in range(len(labs)) for j in range(i + 1, len(labs))) and (len(labs) < 3 or labs not in PAT3)
out = []
for R in range(4, 11):
    for L in range(5, 12):
        T = L * (L - 1) * (L - 2) - 3 * (L - 2) - 4; C2 = math.comb(R - 1, 2)
        g3 = sum(1 for rows in itertools.combinations(range(R), 3) for labs in itertools.permutations(range(L), 3) if ok(labs))
        d = [sum(1 for rows in itertools.combinations(range(R - 1), 2) for labs in itertools.permutations([x for x in range(L) if x != c], 2) if ok(labs + (c,))) for c in range(L)]
        f = [C2 * ((L - 1) * (L - 2) - 1), C2 * (L - 2) * (L - 3), C2 * ((L - 1) * (L - 2) - 2), C2 * ((L - 1) * (L - 2) - 3)] + [C2 * ((L - 1) * (L - 2) - 1)] * (L - 4)
        cap = g3 / (R * L - 1)
        row = dict(R=R, L=L, g3=g3, formula_g3=math.comb(R, 3) * T, d=d, formula_d=f, ceil_cap=math.ceil(cap), d1=d[1],
                   ok=(g3 == math.comb(R, 3) * T and d == f and math.ceil(cap) <= min(d) == d[1]))
        out.append(row)
print('all formulas agree and ceil(cap) <= d_1 = min d_c:', all(r['ok'] for r in out), 'on', len(out), 'boards R=4..10, L=5..11')
print('max ceil(cap)/d_1:', max(r['ceil_cap'] / r['d1'] for r in out))
json.dump(out, open(sys.argv[1], 'w'), indent=1)
