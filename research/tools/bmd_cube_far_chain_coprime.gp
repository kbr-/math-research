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
\\ PAIRS mode (route review bmd-20261004-o): exact roots of T_m and T_(m+1), m = R_l, at (e, l) in PAIRS; the minimum
\\ distance between the two root sets against the minimum spacing inside each (equal-temperament picture: rung
\\ coincidences come within about spacing / m).
PAIRS = getenv("PAIRS");
{
if (PAIRS != 0 && PAIRS != "",
  default(realprecision, 300);
  foreach (eval(PAIRS), el,
    my(e = el[1], l = el[2], m = Rn(l), A = polroots(tpoly(chain(e, l, m), 0)[1]), B = polroots(tpoly(chain(e, l, m + 1), 0)[1]));
    my(inter = vecmin(concat(vector(#A, i, vector(#B, j, abs(A[i] - B[j]))))));
    my(ia = vecmin(concat(vector(#A - 1, i, vector(#A - i, j, abs(A[i] - A[i + j]))))));
    my(ib = vecmin(concat(vector(#B - 1, i, vector(#B - i, j, abs(B[i] - B[j + i]))))));
    emit(Str("PAIRS (e,l)=(", e, ",", l, "), m=", m, ": min |root(T_m) - root(T_(m+1))| = ", precision(inter, 4) * 1.,
      "; min spacing within T_m ", precision(ia, 4) * 1., ", within T_(m+1) ", precision(ib, 4) * 1., "; ratio inter/within ",
      precision(inter / min(ia, ib), 4) * 1.)));
  quit);
}
\\ XSECTOR mode (cycle bmd-20261004-p; lem:cube-far-x-sector-decomposition, conj:cube-far-x-sector-balance): x-side
\\ ladder. With n = R_e, W_k corresponds off {0,-1} to the Casorati determinant det[c_(i,n+s)(r)] of the Taylor
\\ coefficients at x = r of the k' = 1+R_l+4e+4l+4el non-polynomial block functions. The 4l mixed rows
\\ (1+x)^(-5/2) x^(1/2-4l+j) split as c_N = I_0(N) + I_-1(N), I_-1 the integral of f(y)(y-r)^(-N-1)/(2 pi i) over a
\\ hairpin loop around the cut (-oo,-1] (circle of radius RHO about -1), with y^beta cut along [0,oo) (arg in (0,2pi))
\\ and (1+y)^alpha principal. Sector sums E_s = sum over |S| = s of the determinants with the rows in S taking I_0.
\\ At each root r of W_k (sampled, every SKIP-th): |E_s| for s = 0..4l, the two largest indices, the ratio of the third
\\ largest to the largest, and the control |sum E_s| / max |E_s| (vanishes at roots iff the x-side ladder holds).
\\ Orientation and branch control: for the pure row (1+x)^(-7/2) the loop integral must equal its Taylor coefficient.
XSECTOR = getenv("XSECTOR");
brpow(y, b) = exp(b * if (arg(y) < 0, log(y) + 2 * Pi * I, log(y)));
xrows(e, l) = { my(L = List(), Rl = Rn(l));
  listput(L, [-3, 0, 0]);
  for (j = 0, Rl - 1, listput(L, [0, -(Rl + 2) + j, 0]));
  for (j = 0, 4 * e - 1, listput(L, [-7/2, j, 0]));
  for (j = 0, 4 * l - 1, listput(L, [-5/2, 1/2 - 4 * l + j, 1]));
  for (j = 0, 4 * e * l - 1, listput(L, [0, -7/2 + 4 * e - 4 * e * l + j, 0]));
  Vec(L); }
\\ Taylor coefficients c_N, N = N0..N1, of (1+x)^g x^b at r (branches as above)
taylorc(g, b, r, N0, N1) = { my(h = 'h, S = (1 + r)^g * (1 + h / (1 + r) + O(h^(N1 + 1)))^g * brpow(r, b) * (1 + h / r + O(h^(N1 + 1)))^b);
  vector(N1 - N0 + 1, i, polcoef(S, N0 + i - 1, 'h)); }
loopint(g, b, r, N0, N1, rho) = {
  my(del = 1/10, Ap = -1 + rho * exp(I * (Pi - del)), Am = -1 + rho * exp(-I * (Pi - del)));
  my(F = y -> (1 + y)^g * brpow(y, b) * vector(N1 - N0 + 1, i, (y - r)^(-(N0 + i))));
  \\ lower ray from -oo to Am (u = (1-v)/v), circle from angle -(pi-del) to (pi-del), upper ray from Ap to -oo
  my(low = intnum(v = 0, 1, F(Am - (1 - v) / v) / v^2));
  my(circ = intnum(th = -(Pi - del), Pi - del, F(-1 + rho * exp(I * th)) * I * rho * exp(I * th)));
  my(up = -intnum(v = 0, 1, F(Ap - (1 - v) / v) / v^2));
  -(low + circ + up) / (2 * Pi * I); }  \\ the hairpin as parametrized runs clockwise about the cut
\\ Per root r the cuts are the rays from -1 and from 0 pointing directly away from r (distinct rays from the common centre
\\ r, so disjoint); powers are taken with those cuts, so the hairpin keeps distance about |1+r| from r and no precision is
\\ lost. cpow(z, a, u) = z^a with cut along the ray {s u : s > 0} (a fixed constant factor u^a per row).
cpow(z, a, u) = u^a * brpow(z / u, a);
taylorb(g, b, r, u1, u0, N0, N1) = { my(h = 'h, S = cpow(1 + r, g, u1) * (1 + h / (1 + r) + O(h^(N1 + 1)))^g * cpow(r, b, u0) * (1 + h / r + O(h^(N1 + 1)))^b);
  vector(N1 - N0 + 1, i, polcoef(S, N0 + i - 1, 'h)); }
loopb(g, b, r, u1, u0, N0, N1, P = -1) = {
  \\ the hairpin circle must stay clear of the other cut (cycle bmd-20261004-t: the old guard rho < 1/2 let the -1 circle
  \\ cross the 0-cut at a near-collinear root): rho <= half the distance from P to the other ray
  my(uu = if (P == -1, u1, u0), Q = -1 - P, uq = if (P == -1, u0, u1), sq = real((P - Q) * conj(uq)), dq = if (sq > 0, abs(imag((P - Q) * conj(uq))), abs(P - Q)));
  my(rho = min(abs(P - r) / 50, dq / 2), eps = rho / 100, F = y -> cpow(1 + y, g, u1) * cpow(y, b, u0) * vector(N1 - N0 + 1, i, (y - r)^(-(N0 + i))));
  my(Y = w -> P + uu * w, wl = sqrt(rho^2 - eps^2) - I * eps, wu = sqrt(rho^2 - eps^2) + I * eps, th0 = arg(wu));
  \\ in w = (y+1)/u1 the cut is [0, oo): lower ray from +oo to wl, circle through the negative side to wu, upper ray to +oo
  my(low = -intnum(v = 0, 1, F(Y(wl + (1 - v) / v)) * uu / v^2));
  my(circ = intnum(th = -th0, -(2 * Pi - th0), F(Y(rho * exp(I * th))) * uu * I * rho * exp(I * th)));
  my(up = intnum(v = 0, 1, F(Y(wu + (1 - v) / v)) * uu / v^2));
  (low + circ + up) / (2 * Pi * I); }
\\ sector sums E_0..E_nm at the point x (cuts fixed by u1, u0 chosen for a nearby root), sign sg of the hairpin
sectorE(rows, mix, x, u1, u0, n, K, sg) = {
  my(nm = #mix, C = matrix(K, K), I1 = vector(K), E = vector(nm + 1));
  for (i = 1, K, my(tt = taylorb(rows[i][1], rows[i][2], x, u1, u0, n, n + K - 1)); for (s = 1, K, C[i, s] = tt[s]));
  foreach (mix, i, I1[i] = sg * loopb(rows[i][1], rows[i][2], x, u1, u0, n, n + K - 1));
  forsubset (nm, S,
    my(M = C);
    for (a = 1, nm, my(i = mix[a]); if (setsearch(Set(S), a), M[i, ] = C[i, ] - I1[i], M[i, ] = I1[i]));
    E[#S + 1] += matdet(M));
  E; }
\\ XCONCAVE mode (cycle bmd-20261004-v; conj:cube-far-sector-concavity): at every SKIP-th non-real root of W_(b-1),
\\ the second differences D2(s) = log|E_(s+1)| - 2 log|E_s| + log|E_(s-1)|, s = 1..4l-1, against the cluster prediction
\\ -4 log(n+1) + 2 log|r(1+r)|; concavity (all D2 < 0) makes only adjacent sums able to tie.
XCONCAVE = getenv("XCONCAVE");
{
if (XCONCAVE != 0 && XCONCAVE != "",
  default(realprecision, if (getenv("PREC") != "" && getenv("PREC") != 0, eval(getenv("PREC")), 160));
  my(skip = if (getenv("SKIP") != "" && getenv("SKIP") != 0, eval(getenv("SKIP")), 1));
  foreach (eval(XCONCAVE), el,
    my(e = el[1], l = el[2], n = Rn(e), rows = xrows(e, l), K = #rows, T = tpoly(chain(e, l, Rn(l)), 0)[1], rt = polroots(T));
    my(mix = select(i -> rows[i][3] == 1, [1..K]), nm = #mix, out = List());
    forstep (q = 1, #rt, skip,
      my(r = rt[q]); if (abs(imag(r)) < 10^-20, next);
      my(u1 = (-1 - r) / abs(1 + r), u0 = -r / abs(r));
      my(cc = taylorb(-7/2, 0, r, u1, u0, n, n + 3), ci = loopb(-7/2, 0, r, u1, u0, n, n + 3), sg = if (normlp(ci + cc) < normlp(ci - cc), -1, 1));
      my(E = sectorE(rows, mix, r, u1, u0, n, K, sg), L = apply(z -> log(abs(z)), E), A = apply(abs, E), srt = vecsort(A, , 5));
      my(pred = -4 * log(n + 1) + 2 * log(abs(r * (1 + r))));
      listput(out, [precision(log(abs(r / (1 + r))), 4) * 1., srt[1] - 1, srt[2] - 1, precision(pred, 4) * 1., vector(nm - 1, s, precision(L[s + 2] - 2 * L[s + 1] + L[s], 4) * 1.)]));
    emit(Str("XCONCAVE (e,l)=(", e, ",", l, "): n=", n, "; per root [log|t|, largest s, second s, predicted D2, [D2(1..", nm - 1, ")]]: ", Vec(out))));
  quit);
}
\\ XLAPLACE mode (cycle bmd-20261004-r): is each sector sum E_s dominated by one contiguous Laplace term? For every
\\ subset S of mixed rows, D_S splits by rows into the 0-sector (pure rows without a (1+x) factor, and the mixed rows of S
\\ with their I_0 parts) and the (-1)-sector. L_s^top (L_s^bot) sums over |S| = s the Laplace terms in which the 0-sector
\\ rows take the top (bottom) columns, with the Laplace sign. At balanced roots, report |L_s^top/E_s - 1| and
\\ |L_s^bot/E_s - 1| for the two balancing sums.
laplaceE(rows, mix, x, u1, u0, n, K, sg) = {
  my(nm = #mix, C = matrix(K, K), I1 = vector(K), E = vector(nm + 1), Lt = vector(nm + 1), Lb = vector(nm + 1));
  for (i = 1, K, my(tt = taylorb(rows[i][1], rows[i][2], x, u1, u0, n, n + K - 1)); for (s = 1, K, C[i, s] = tt[s]));
  foreach (mix, i, I1[i] = sg * loopb(rows[i][1], rows[i][2], x, u1, u0, n, n + K - 1));
  forsubset (nm, S,
    my(M = C, z = List(), o = List());
    for (a = 1, nm, my(i = mix[a]); if (setsearch(Set(S), a), M[i, ] = C[i, ] - I1[i], M[i, ] = I1[i]));
    for (i = 1, K, if (rows[i][3] == 1, if (setsearch(Set(S), select(a -> mix[a] == i, [1..nm])[1]), listput(z, i), listput(o, i)), if (rows[i][1] == 0, listput(z, i), listput(o, i))));
    z = Vec(z); o = Vec(o);
    my(a = #z, P = concat(z, o), sgn = permsign(Vecsmall(P)));
    \\ rows reordered as (z, o): det M = sgn * det(M[P,]); Laplace: top columns for z means columns K-a+1..K
    my(Mz = matrix(a, K, i, j, M[z[i], j]), Mo = matrix(K - a, K, i, j, M[o[i], j]));
    my(top = (-1)^(a * (K - a)) * matdet(matrix(a, a, i, j, Mz[i, K - a + j])) * matdet(matrix(K - a, K - a, i, j, Mo[i, j])));
    my(bot = matdet(matrix(a, a, i, j, Mz[i, j])) * matdet(matrix(K - a, K - a, i, j, Mo[i, a + j])));
    E[#S + 1] += matdet(M); Lt[#S + 1] += sgn * top; Lb[#S + 1] += sgn * bot);
  [E, Lt, Lb]; }
XLAPLACE = getenv("XLAPLACE");
{
if (XLAPLACE != 0 && XLAPLACE != "",
  default(realprecision, if (getenv("PREC") != "" && getenv("PREC") != 0, eval(getenv("PREC")), 160));
  my(skip = if (getenv("SKIP") != "" && getenv("SKIP") != 0, eval(getenv("SKIP")), 1));
  foreach (eval(XLAPLACE), el,
    my(e = el[1], l = el[2], n = Rn(e), rows = xrows(e, l), K = #rows, T = tpoly(chain(e, l, Rn(l)), 0)[1], rt = polroots(T));
    my(mix = select(i -> rows[i][3] == 1, [1..K]), out = List());
    forstep (q = 1, #rt, skip,
      my(r = rt[q]); if (abs(imag(r)) < 10^-20, next);
      my(u1 = (-1 - r) / abs(1 + r), u0 = -r / abs(r));
      my(cc = taylorb(-7/2, 0, r, u1, u0, n, n + 3), ci = loopb(-7/2, 0, r, u1, u0, n, n + 3), sg = if (normlp(ci + cc) < normlp(ci - cc), -1, 1));
      my(R3 = laplaceE(rows, mix, r, u1, u0, n, K, sg), E = R3[1], A = apply(abs, E), srt = vecsort(A, , 5));
      if (abs(srt[1] - srt[2]) != 1 || A[srt[3]] / A[srt[1]] > 10^-3, next);
      my(dev = v -> precision(log(abs(v)) / log(10), 3) * 1.);
      listput(out, [precision(log(abs(r / (1 + r))), 4) * 1., min(srt[1], srt[2]) - 1,
        vector(2, k, my(s = srt[k]); [dev(R3[2][s] / E[s] - 1), dev(R3[3][s] / E[s] - 1)])]));
    emit(Str("XLAPLACE (e,l)=(", e, ",", l, "): per balanced root [log|t|, i, for E_i and E_(i+1) by size: [log10|L^top/E - 1|, log10|L^bot/E - 1|]]: ", Vec(out))));
  quit);
}
\\ XDERIV mode (cycle bmd-20261004-q; conj:cube-far-x-sector-ratio): at sampled non-real roots r of W_(b-1) with a
\\ two-term balance (third/largest <= 1e-3), kappa = r(1+r) d/dr log(E_(i+1)/E_i) for the dominant pair, by a central
\\ difference with step H = 10^-30 and the cuts of r; the prediction is kappa = -(R_e + 7/2) (sector step t^-N, N = n+7/2).
XDERIV = getenv("XDERIV");
{
if (XDERIV != 0 && XDERIV != "",
  default(realprecision, if (getenv("PREC") != "" && getenv("PREC") != 0, eval(getenv("PREC")), 160));
  my(skip = if (getenv("SKIP") != "" && getenv("SKIP") != 0, eval(getenv("SKIP")), 1), hh = 10^-30);
  foreach (eval(XDERIV), el,
    my(e = el[1], l = el[2], n = Rn(e), rows = xrows(e, l), K = #rows, T = tpoly(chain(e, l, Rn(l)), 0)[1], rt = polroots(T));
    my(mix = select(i -> rows[i][3] == 1, [1..K]), out = List());
    forstep (q = 1, #rt, skip,
      my(r = rt[q]); if (abs(imag(r)) < 10^-20, next);
      my(u1 = (-1 - r) / abs(1 + r), u0 = -r / abs(r));
      my(cc = taylorb(-7/2, 0, r, u1, u0, n, n + 3), ci = loopb(-7/2, 0, r, u1, u0, n, n + 3), sg = if (normlp(ci + cc) < normlp(ci - cc), -1, 1));
      my(E = sectorE(rows, mix, r, u1, u0, n, K, sg), A = apply(abs, E), srt = vecsort(A, , 5));
      if (abs(srt[1] - srt[2]) != 1 || A[srt[3]] / A[srt[1]] > 10^-3, next);
      my(i = min(srt[1], srt[2]), Ep = sectorE(rows, mix, r + hh, u1, u0, n, K, sg), Em = sectorE(rows, mix, r - hh, u1, u0, n, K, sg));
      my(dl = log((Ep[i + 1] / Ep[i]) / (Em[i + 1] / Em[i])) / (2 * hh), kap = r * (1 + r) * dl);  \\ one log of the quotient: no branch jump
      my(mu = kap + (n + 7/2) + r);  \\ cycle bmd-20261004-r: the j = 0 mixed row predicts kappa = -(n+7/2) - r
      listput(out, [precision(log(abs(r / (1 + r))), 4) * 1., i - 1, precision(real(kap), 6) * 1., precision(imag(kap), 4) * 1., precision(real(r), 4) * 1., precision(imag(r), 4) * 1., precision(real(mu), 4) * 1., precision(imag(mu), 4) * 1.]));
    emit(Str("XDERIV (e,l)=(", e, ",", l, "): n=R_e=", n, ", predicted kappa = -(n+7/2) = ", -(n + 7/2),
      "; per balanced root [log|t|, i (pair E_i, E_(i+1)), Re kappa, Im kappa, Re r, Im r, Re mu, Im mu] with mu = kappa + n + 7/2 + r: ", Vec(out))));
  quit);
}
{
if (XSECTOR != 0 && XSECTOR != "",
  default(realprecision, if (getenv("PREC") != "" && getenv("PREC") != 0, eval(getenv("PREC")), 80));
  my(skip = if (getenv("SKIP") != "" && getenv("SKIP") != 0, eval(getenv("SKIP")), 1));
  foreach (eval(XSECTOR), el,
    my(e = el[1], l = el[2], n = Rn(e), rows = xrows(e, l), K = #rows, T = tpoly(chain(e, l, Rn(l)), 0)[1], rt = polroots(T));
    my(mix = select(i -> rows[i][3] == 1, [1..K]), nm = #mix, out = List(), ctl = 0., cerr = 0., serr = 0., nreal = 0);
    forstep (q = 1, #rt, skip,
      my(r = rt[q], u1 = (-1 - r) / abs(1 + r), u0 = -r / abs(r));
      if (abs(imag(r)) < 10^-20, nreal++; next);
      my(cc = taylorb(-7/2, 0, r, u1, u0, n, n + 3), ci = loopb(-7/2, 0, r, u1, u0, n, n + 3), sg = 1);
      \\ orientation fixed once by the control row, then its error recorded
      if (normlp(ci + cc) < normlp(ci - cc), sg = -1);
      cerr = max(cerr, normlp(sg * ci - cc) / normlp(cc));
      my(C = matrix(K, K), I1 = vector(K));
      for (i = 1, K, my(tt = taylorb(rows[i][1], rows[i][2], r, u1, u0, n, n + K - 1)); for (s = 1, K, C[i, s] = tt[s]));
      foreach (mix, i, I1[i] = sg * loopb(rows[i][1], rows[i][2], r, u1, u0, n, n + K - 1));
      my(i1 = mix[1], z0 = sg * loopb(rows[i1][1], rows[i1][2], r, u1, u0, n, n + 3, 0), cz = taylorb(rows[i1][1], rows[i1][2], r, u1, u0, n, n + 3));
      my(se = normlp(I1[i1][1..4] + z0 - cz) / normlp(cz)); serr = max(serr, se);  \\ per-root split error (cycle bmd-20261004-t)
      my(E = vector(nm + 1));
      forsubset (nm, S,
        my(M = C);
        for (a = 1, nm, my(i = mix[a]); if (setsearch(Set(S), a), M[i, ] = C[i, ] - I1[i], M[i, ] = I1[i]));
        E[#S + 1] += matdet(M));
      my(A = apply(abs, E), srt = vecsort(A, , 5), mx = A[srt[1]]);
      my(cr = abs(vecsum(E)) / mx); ctl = max(ctl, cr);
      listput(out, [precision(log(abs(r / (1 + r))), 4) * 1., srt[1] - 1, srt[2] - 1, precision(A[srt[3]] / mx, 4) * 1., precision(cr, 3) * 1., precision(se, 3) * 1., precision(real(r), 4) * 1., precision(imag(r), 4) * 1.]));
    emit(Str("XSECTOR (e,l)=(", e, ",", l, "): n=R_e=", n, ", rows ", K, ", mixed ", nm, ", deg W ", poldegree(T),
      "; max control error of the loop on (1+x)^(-7/2): ", precision(cerr, 4) * 1., "; max split error |I_-1 + I_0 - c| / |c| on the first mixed row (0-cut hairpin): ", precision(serr, 4) * 1., "; real roots skipped: ", nreal));
    emit(Str("  per sampled root [log|t|, largest s, second s, third/largest, |sum E_s|/max|E_s|, split error, Re r, Im r]: ", Vec(out)));
    emit(Str("  max |sum E_s| / max|E_s| = ", precision(ctl, 4) * 1.)));
  quit);
}
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
