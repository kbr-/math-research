\\ A-chain coprimality of far Wronskians (4 October 2026; route review bmd-20261004-k).
\\ Far component of even-peeling step (e, l): blocks (1+x)^g x^b P_<cnt,
\\   [g,b,cnt] = [0,0,R_e],[-3,0,1],[0,-(R_l+2),R_l],[-7/2,0,4e],[-5/2,1/2-4l,4l],[0,-7/2+4e-4el,4el].
\\ T_m: the same space with the A-block [0,-(m+2),m] (exponents -(m+2)..-3), so T_(R_l) = W_k;
\\ Q_A: the A-block with its lowest element x^-(R_l+2) replaced by x^-(R_l+3) (lem:cube-far-first-order-splitting).
\\ Jacobi (Desnanot) identity with S = T_(m-1)-space, g = x^-(m+2), h = x^-(m+3):
\\   Wr(Wr(S,g), Wr(S,h)) = Wr(S) Wr(S,g,h), i.e. T_(m-1) T_(m+1) = Wr(T_m, Q_A) up to powers of x and 1+x.
\\ Tested statement (review test): a common root r (r != 0, -1) of T_m and Q_A is a root of T_(m-1) T_(m+1);
\\ so gcd(T_m, T_(m-1)) = gcd(T_m, T_(m+1)) = 1 implies gcd(T_m, Q_A) = 1, which gives the first-order criterion
\\ at every multiple root. Reports degrees, the three gcds and squarefreeness, modulo q = 2^61 - 1, and checks the
\\ identity at random points as a control.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
Rn(n) = n * (2 * n - 1);
base(e, l) = [[0, 0, Rn(e)], [-3, 0, 1], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]];
chain(e, l, m) = concat(base(e, l), [[0, -(m + 2), m]]);
qa(e, l) = my(r = Rn(l)); concat(base(e, l), [[0, -(r + 3), 1], [0, -(r + 1), r - 1]]);
\\ Taylor row at x0 of (1+x)^ga x^(be+j), with x0^be (1+x0)^ga removed (as in bmd_cube_far_first_order.gp, c = 1)
mq(z, q) = if (q, Mod(z, q), z);
rowf(ga, be, j, x0, R, q) = {
  my(u = vector(R, a, mq(binomial(be + j, a - 1), q) * x0^(j - a + 1)), r = mq(1, q) / (1 + x0));
  my(v = vector(R, s, mq(binomial(ga, s - 1), q) * r^(s - 1)));
  vector(R, m, sum(a = 1, m, u[a] * v[m + 1 - a]));
}
dval(B, x0, q) = {
  my(R = sum(k = 1, #B, B[k][3]), rows = List());
  foreach (B, b, for (j = 0, b[3] - 1, listput(rows, rowf(b[1], b[2], j, x0, R, q))));
  matdet(Mat(Vec(rows)~));
}
\\ local exponents of the block space at P = 0 (u = x) or P = -1 (u = 1+x): pivots per class, modulo q
pivots(M, q) = {
  my(A = if (q, M * Mod(1, q), M), E = matrix(#M~, 0), r = 0, piv = List());
  for (k = 1, #M, my(E2 = matconcat([E, A[, k]])); if (matrank(E2) > r, E = E2; r++; listput(piv, k); if (r == #M~, break)));
  Vec(piv);
}
expsum(B, P, q) = {
  my(R = sum(k = 1, #B, B[k][3]), N = 3 * R + 20, F = List(), tot = 0);
  foreach (B, b, for (j = 0, b[3] - 1,
    if (P == 0, listput(F, [b[2] + j, (1 + 'u + O('u^N))^b[1]]), listput(F, [b[1], (-1 + 'u + O('u^N))^(b[2] + j)]))));
  F = Vec(F);
  foreach (Set(apply(f -> frac(f[1]), F)), c,
    my(G = select(f -> frac(f[1]) == c, F), m0 = vecmin(apply(f -> f[1], G)), C = N - 5, M = matrix(#G, C));
    for (i = 1, #G, my(s = G[i][2] * 'u^(G[i][1] - m0)); for (k = 0, C - 1, M[i, k + 1] = polcoef(s, k, 'u)));
    my(pv = pivots(M, q)); if (#pv < #G, error("rank deficient class"));
    tot += sum(i = 1, #pv, m0 + pv[i] - 1));
  tot;
}
\\ T = W x^-ord0 (1+x)^-ord_-1, a polynomial; W(x0) = dval(x0) x0^Sb (1+x0)^Sg up to a constant; returns [T, ord0, ord_-1]
tpoly(B, q) = {
  my(R = sum(k = 1, #B, B[k][3]), bin = binomial(R, 2), o0 = expsum(B, 0, q) - bin, o1 = expsum(B, -1, q) - bin);
  my(Sb = sum(k = 1, #B, B[k][2] * B[k][3]), Sg = sum(k = 1, #B, B[k][1] * B[k][3]), a = Sb - o0, c = Sg - o1);
  if (denominator(a) != 1 || denominator(c) != 1, error("non-integral normalization"));
  my(dm = 64);
  while (dm <= 4096,
    my(xs = vector(dm + 3, i, mq(i + 1, q)), ys = vector(dm + 3, i, dval(B, lift(xs[i]), q) * xs[i]^a * (1 + xs[i])^c));
    my(P = polinterpolate(xs[1..dm + 1], ys[1..dm + 1], 'x));
    if (subst(P, 'x, xs[dm + 2]) == ys[dm + 2] && subst(P, 'x, xs[dm + 3]) == ys[dm + 3],
      if (polcoef(P, 0) == 0 || subst(P, 'x, mq(-1, q)) == 0, error("normalization left a factor x or 1+x"));
      return([P, o0, o1]));
    dm *= 2);
  error("interpolation failed");
}
dg(P) = poldegree(P);
\\ TESTS mode (route review bmd-20261004-k), at (e, l) in TESTS, modulo q:
\\  (a) three-term recurrence: is T_(m+1) = A T_m + B T_(m-1) with deg A <= 4e, deg B <= 8e solvable (Favard-type chain)?
\\  (b) Adler-Moser-type identity: deg gcd(T_m, [Wr(T_(m-1), T_(m+1))]) with the prefactors x^a (1+x)^c included, and
\\      whether T_m^2 divides it (as in Wr(theta_(n-1), theta_(n+1)) = (2n+1) theta_n^2).
\\ EXACT mode, at (e, l) in EXACT, over Q: resultant of T_m and T_(m+1) (m = R_l), and discriminant of T_m as a control;
\\ prime factors below 10^5 and the size of the unfactored cofactor (a product formula leaves cofactor 1).
brk(A, B) = 'x * (1 + 'x) * (A[1] * deriv(B[1]) - deriv(A[1]) * B[1]) + ((B[2] - A[2]) * (1 + 'x) + (B[3] - A[3]) * 'x) * A[1] * B[1];
TESTS = getenv("TESTS"); EXACT = getenv("EXACT"); LADDER = getenv("LADDER");
\\ LADDER mode (cycle bmd-20261004-l; lem:cube-far-derivative-ladder): in y = 1/x the A-block x^-(m+2) P_<m is
\\ y^3 P_<m(y), so T_m is the Wronskian of P_<m + Psi with Psi = y^-3 U (blocks below, same [g, b, cnt] format in y),
\\ that is of the m-th derivatives of Psi. Control: the y-side polynomial is proportional to the reversal of T_m.
\\ ROOTS mode (cycle bmd-20261004-n; conj:cube-far-sector-circles): exact T_(R_l) over Q at (e, l) in ROOTS, its complex
\\ roots, and the moduli |1+x| sorted, grouped where consecutive log-moduli differ by more than GAP (default 0.05); the
\\ sector expansion predicts 4e groups of about R_l roots each near circles |1+x| = rho_i for l large against e.
ROOTS = getenv("ROOTS");
{
if (ROOTS != 0 && ROOTS != "",
  default(realprecision, 300);
  my(gap = if (getenv("GAP") != "" && getenv("GAP") != 0, eval(getenv("GAP")), 0.05));
  foreach (eval(ROOTS), el,
    my(e = el[1], l = el[2], m = Rn(l), T = tpoly(chain(e, l, m), 0)[1], rt = polroots(T));
    my(v = vecsort(apply(z -> log(abs(1 + z)), rt)), groups = List(), cur = [v[1], v[1], 1]);
    for (i = 2, #v, if (v[i] - v[i - 1] > gap, listput(groups, cur); cur = [v[i], v[i], 1], cur[2] = v[i]; cur[3]++));
    listput(groups, cur);
    emit(Str("ROOTS (e,l)=(", e, ",", l, "), m=R_l=", m, ", deg T=", poldegree(T), ", 4e m=", 4 * e * m,
      ": groups of log|1+x| [min, max, count]: ", apply(g -> [precision(g[1], 4) * 1., precision(g[2], 4) * 1., g[3]], Vec(groups))));
    \\ also |x/(1+x)| for comparison with the last-step circle law
    my(t = vecsort(apply(z -> log(abs(z / (1 + z))), rt)));
    emit(Str("  log|x/(1+x)| range: [", precision(t[1], 4) * 1., ", ", precision(t[#t], 4) * 1., "]; min |root spacing| ",
      precision(vecmin(concat(vector(#rt, i, vector(#rt - i, j, abs(rt[i] - rt[i + j]))))), 4) * 1.)));
  quit);
}
psiblk(e, l) =[[0, -Rn(e) - 2, Rn(e)], [-3, 0, 1], [-7/2, 3/2 - 4 * e, 4 * e], [-5/2, 0, 4 * l], [0, 3/2 - 4 * e, 4 * e * l]];
{
if (LADDER != 0 && LADDER != "",
  my(q = 2^61 - 1);
  foreach (eval(LADDER), el,
    my(e = el[1], l = el[2], res = List());
    for (m = Rn(l) - 1, Rn(l) + 1,
      my(Tx = tpoly(chain(e, l, m), q)[1], Ty = tpoly(concat([[0, 0, m]], psiblk(e, l)), q)[1], Rx = polrecip(Tx));
      listput(res, [m, dg(Tx), dg(Ty), dg(Rx) == dg(Ty) && pollead(Ty) * Rx == pollead(Rx) * Ty]));
    emit(Str("LADDER (e,l)=(", e, ",", l, "): [m, deg T_m (x side), deg (y side), proportional to the reversal]: ", Vec(res))));
  quit);
}
{
if (TESTS != 0 && TESTS != "",
  my(q = 2^61 - 1);
  foreach (eval(TESTS), el,
    my(e = el[1], l = el[2], m = Rn(l), Am = tpoly(chain(e, l, m - 1), q), A0 = tpoly(chain(e, l, m), q), Ap = tpoly(chain(e, l, m + 1), q));
    my(da = 4 * e, db = 8 * e, n = dg(Ap[1]) + 1, M = matrix(n, da + db + 2), rhs = vectorv(n, i, polcoef(Ap[1], i - 1)));
    for (j = 0, da, my(P = 'x^j * A0[1]); for (i = 1, n, M[i, j + 1] = polcoef(P, i - 1)));
    for (j = 0, db, my(P = 'x^j * Am[1]); for (i = 1, n, M[i, da + 2 + j] = polcoef(P, i - 1)));
    my(rk = matrank(M), rk2 = matrank(matconcat([M, rhs])));
    my(Bk = brk(Am, Ap), g = gcd(Bk, A0[1]), sq = (Bk % (A0[1]^2) == 0));
    emit(Str("TESTS (e,l)=(", e, ",", l, "), m=", m, ": recurrence T_(m+1) = A T_m + B T_(m-1), deg A<=", da, ", deg B<=", db,
      ": rank ", rk, " -> ", rk2, if (rk2 > rk, " (no solution)", " (solvable)"), "; deg Wr(T_(m-1),T_(m+1)) bracket ", dg(Bk),
      ", deg gcd with T_m ", dg(g), " of ", dg(A0[1]), ", divisible by T_m^2: ", sq)));
  if (EXACT == 0 || EXACT == "", quit));
if (EXACT != 0 && EXACT != "",
  foreach (eval(EXACT), el,
    my(e = el[1], l = el[2], m = Rn(l), T0 = tpoly(chain(e, l, m), 0)[1], Tp = tpoly(chain(e, l, m + 1), 0)[1]);
    T0 = T0 / content(T0); Tp = Tp / content(Tp);
    my(R = polresultant(T0, Tp), D = poldisc(T0));
    foreach ([["Res(T_m,T_(m+1))", R], ["disc(T_m)", D]], pr,
      my(v = abs(pr[2]), F = factor(v, 10^5), small = List(), cof = 1);
      for (i = 1, #F~, if (F[i, 1] < 10^5, listput(small, [F[i, 1], F[i, 2]]), cof *= F[i, 1]^F[i, 2]));
      emit(Str("EXACT (e,l)=(", e, ",", l, "), m=", m, ", deg T_m=", dg(T0), ", deg T_(m+1)=", dg(Tp), ": ", pr[1], " has ",
        #Str(v), " digits; primes < 10^5 with exponents: ", Vec(small), "; unfactored cofactor ", #Str(cof), " digits"))));
  quit);
}
{
my(q = 2^61 - 1, cases = eval(getenv("CASES")));
foreach (cases, el,
  my(e = el[1], l = el[2], m = Rn(l), Am = tpoly(chain(e, l, m - 1), q), A0 = tpoly(chain(e, l, m), q), Ap = tpoly(chain(e, l, m + 1), q), AQ = tpoly(qa(e, l), q));
  my(Tm = Am[1], T0 = A0[1], Tp = Ap[1], Q = AQ[1]);
  \\ control: Wr(x^a1 (1+x)^c1 T_m, x^a2 (1+x)^c2 Q) = x^(a1+a2-1) (1+x)^(c1+c2-1) [x(1+x)(T_m Q' - T_m' Q)
  \\ + ((a2-a1)(1+x) + (c2-c1) x) T_m Q]; the identity says the bracket is a constant times
  \\ x^(a3+a4-a1-a2+1) (1+x)^(c3+c4-c1-c2+1) T_(m-1) T_(m+1), with (a3,c3), (a4,c4) the orders of T_(m-1), T_(m+1)
  my(Wq = 'x * (1 + 'x) * (T0 * deriv(Q) - deriv(T0) * Q) + ((AQ[2] - A0[2]) * (1 + 'x) + (AQ[3] - A0[3]) * 'x) * T0 * Q);
  my(sx = Am[2] + Ap[2] - A0[2] - AQ[2] + 1, t = Am[3] + Ap[3] - A0[3] - AQ[3] + 1);
  my(L = Tm * Tp * 'x^sx * (1 + 'x)^t, ok = (sx >= 0) && (t >= 0) && (dg(L) == dg(Wq)) && (pollead(Wq) * L == pollead(L) * Wq));
  emit(Str("(e,l)=(", e, ",", l, "), m=R_l=", m, ": deg T_(m-1), T_m, T_(m+1), Q_A = ", [dg(Tm), dg(T0), dg(Tp), dg(Q)],
    "; identity T_(m-1)T_(m+1) ~ Wr(T_m,Q_A) (stripped x^", sx, " (1+x)^", t, "): ", ok,
    "; deg gcd(T_m,T_(m-1)) ", dg(gcd(T0, Tm)), ", gcd(T_m,T_(m+1)) ", dg(gcd(T0, Tp)), ", gcd(T_m,Q_A) ", dg(gcd(T0, Q)),
    "; squarefree T_(m-1),T_m,T_(m+1): ", [dg(gcd(Tm, deriv(Tm))), dg(gcd(T0, deriv(T0))), dg(gcd(Tp, deriv(Tp)))])));
}
