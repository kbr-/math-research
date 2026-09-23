"""Numerical check of the two component identities behind the degree-four spread lemma (weak unary PHP top algebra
over F_3, n holes).  For random quadratic q and linear l, p = q*l^2 (collision-free monomials):
 (I4)  on four distinct pigeons a,b,c,d with disjoint label pairs, the mixed fourth difference of p equals
       2 * sum over the six splits {X,Y} of H_X(P_X) * delta f_Y(P_Y), H_xy the mixed second difference of q_xy;
 (IR)  on {a,a,c,d}, the alternating 4-cycle difference (e12 - e24 + e43 - e31) in the a-edge, times first differences
       in c and d, equals 2*[box q_aa df_c df_d + (H_ac(P,P_c) df_a(P') + df_a(P) H_ac(P',P_c)) df_d
       + (H_ad(P,P_d) df_a(P') + df_a(P) H_ad(P',P_d)) df_c + H_cd df_a(P) df_a(P')], with P=(1,4), P'=(2,3).
Also checks that both operators vanish on relation products R_i*m.  Usage: --n N --trials T"""
import argparse, itertools, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a4lib as L
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=8); ap.add_argument('--trials', type=int, default=200)
opt = ap.parse_args(); L.setup(opt.n); n = opt.n; P1 = n + 1; rng = np.random.default_rng(1)
X = lambda i, j: i * n + j
def coef(p, *vs): return p.get(tuple(sorted(vs)), 0)
def rand_quad():
    return {m: int(rng.integers(0, 3)) for m in itertools.combinations(range(L.v), 2) if L.hole(m[0]) != L.hole(m[1])}
def D4(p, a, b, c, d, Pa, Pb, Pc, Pd):
    s = 0
    for e in itertools.product((0, 1), repeat=4):
        s += (-1) ** sum(e) * coef(p, X(a, Pa[e[0]]), X(b, Pb[e[1]]), X(c, Pc[e[2]]), X(d, Pd[e[3]]))
    return s % 3
def BOX(p, a, c, d, lab, Pc, Pd):
    j1, j2, j3, j4 = lab; s = 0
    for sg, (u, w) in ((1, (j1, j2)), (-1, (j2, j4)), (1, (j4, j3)), (-1, (j3, j1))):
        for e in itertools.product((0, 1), repeat=2):
            s += sg * (-1) ** sum(e) * coef(p, X(a, u), X(a, w), X(c, Pc[e[0]]), X(d, Pd[e[1]]))
    return s % 3
bad = [0, 0, 0, 0]; tested_box = 0; tested_star = 0
for t in range(opt.trials):
    q = rand_quad(); l = rng.integers(0, 3, size=L.v); p = L.mul(q, L.square(l))
    f = lambda i, j: int(l[X(i, j)]); df = lambda i, P: f(i, P[0]) - f(i, P[1])
    H = lambda x, y, P, Q: sum((-1) ** (e0 + e1) * coef(q, X(x, P[e0]), X(y, Q[e1])) for e0 in (0, 1) for e1 in (0, 1))
    a, b, c, d = rng.choice(P1, 4, replace=False); labs = rng.permutation(n)[:8]
    Pa, Pb, Pc, Pd = labs[0:2], labs[2:4], labs[4:6], labs[6:8]
    Ps = {a: Pa, b: Pb, c: Pc, d: Pd}
    rhs = sum(H(x, y, Ps[x], Ps[y]) * df(z, Ps[z]) * df(w, Ps[w])
              for (x, y), (z, w) in [((a, b), (c, d)), ((c, d), (a, b)), ((a, c), (b, d)), ((b, d), (a, c)), ((a, d), (b, c)), ((b, c), (a, d))])
    bad[0] += (D4(p, a, b, c, d, Pa, Pb, Pc, Pd) - 2 * rhs) % 3 != 0
    lab = labs[0:4]; P, Pp = (lab[0], lab[3]), (lab[1], lab[2])
    qaa = lambda u, w: coef(q, X(a, u), X(a, w))
    box = (qaa(lab[0], lab[1]) - qaa(lab[1], lab[3]) + qaa(lab[3], lab[2]) - qaa(lab[2], lab[0]))
    rhs2 = (box * df(c, Pc) * df(d, Pd) + (H(a, c, P, Pc) * df(a, Pp) + df(a, P) * H(a, c, Pp, Pc)) * df(d, Pd)
            + (H(a, d, P, Pd) * df(a, Pp) + df(a, P) * H(a, d, Pp, Pd)) * df(c, Pc) + H(c, d, Pc, Pd) * df(a, P) * df(a, Pp))
    bad[1] += (BOX(p, a, c, d, lab, Pc, Pd) - 2 * rhs2) % 3 != 0
    # relations: R_i * m for a random collision-free cubic m in the right component
    i = int(rng.choice([a, b, c, d])); others = [y for y in (a, b, c, d) if y != i]
    hs = rng.permutation(n)[:3]; m = tuple(X(y, int(h)) for y, h in zip(others, hs))
    R = {tuple(sorted(m + (X(i, j),))): 1 for j in range(n) if j not in hs}
    bad[2] += D4(R, a, b, c, d, Pa, Pb, Pc, Pd) != 0
    i = int(rng.choice([a, c, d])); hs = rng.permutation(n)[:4]
    mm = {a: [X(a, int(hs[0])), X(a, int(hs[1]))] if i != a else [X(a, int(hs[0]))], c: [X(c, int(hs[2]))], d: [X(d, int(hs[3]))]}
    cub = tuple(u for y in (a, c, d) for u in (mm[y] if y != i else ([mm[y][0]] if y == a else [])))
    cub = tuple(sorted(set(cub)))
    if len({L.hole(u) for u in cub}) == 3:
        R2 = {tuple(sorted(cub + (X(i, j),))): 1 for j in range(n) if j not in {L.hole(u) for u in cub}}
        bad[3] += BOX(R2, a, c, d, lab, Pc, Pd) != 0; tested_box += 1; tested_star += (i == a)
print(dict(n=n, trials=opt.trials, I4_failures=bad[0], IR_failures=bad[1], D4_on_relations_nonzero=bad[2], BOX_on_relations_nonzero=bad[3], BOX_relation_cases_tested=tested_box, BOX_star_cases_tested=tested_star))
