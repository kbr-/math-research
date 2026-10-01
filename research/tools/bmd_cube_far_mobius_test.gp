\\ Moebius test of the first-order far correction (3 October 2026; cycle bmd-20261003-ze).
\\ lem:cube-far-first-order-splitting: far Wronskian (normalized like W_k) = W_k + eps R_1 + O(eps^2),
\\ R_1 = G_A Q_A + G_B Q_B + G_C Q_C, Q_X = Wronskian of F_k with the top element of class X multiplied by x^-1.
\\ Question: is R_1 = v W_k' (mod W_k) with deg v <= 2 (a Moebius vector field), which would make R_1 vanish at every
\\ multiple root of W_k?  Prediction: yes for l = 1 (exact Moebius orbit, proved in the entry): positive control.
\\ For l >= 2 the answer decides whether the first-order splitting lemma can ever help.
\\ Method: modulo q = 2^61 - 1, c as in the far-components script; Q_X normalized exactly like W_k:
\\   W_k(x0) = D_0(x0) x0^A0 (1+c x0)^Ac,  Q_X(x0) = D_X(x0) x0^(A0-1) (1+c x0)^Ac  (rows divided by x0^be (1+cx0)^ga).
\\ Polynomial versions P_X = Q_X x^s (1+cx)^t, then S = R_1 / W_k' mod W_k computed as
\\   (sum G_X P_X) * (x^s (1+cx)^t W_k')^(-1) mod W_k; report deg S (deg <= 2 means Moebius).
\\ G_X from the exact formulas of bmd_cube_far_first_order_g.gp at one D.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
blocks(e, l) = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Rn(l) + 2), Rn(l)], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]];
rowf(ga, be, j, c, x0, R, q) = {
  my(u = vector(R, a, Mod(binomial(be + j, a - 1), q) * x0^(j - a + 1)), r = Mod(c, q) / (1 + c * x0));
  my(v = vector(R, s, Mod(binomial(ga, s - 1), q) * r^(s - 1)));
  vector(R, m, sum(a = 1, m, u[a] * v[m + 1 - a]));
}
Dval(e, l, c, x0, q, swap) = {
  my(R = Rn(e + l + 1), rows = List(), bl = blocks(e, l));
  for (k = 1, #bl, for (j = 0, bl[k][3] - 1, listput(rows, rowf(bl[k][1], bl[k][2] - (k == swap && j == 0), j, c, x0, R, q))));
  matdet(Mat(Vec(rows)~));
}
export(Rn, blocks, rowf, Dval);
md(N, c) = my(K = 2 * N - 4); -c * K + binomial(K, 2) - 3 + binomial(binomial(N - 2, 2), 2);
sum0(e, l) = -sum(j = 3, Rn(l) + 2, j) + sum(j = 0, Rn(e) + 4 * e, j) + sum(i = 4 * e - 4 * e * l, 4 * e + 4 * l - 1, i - 7/2);
sumatinf(e, l) = -binomial(Rn(e), 2) + sum(j = 3, Rn(l) + 4 * l + 3, j) + sum(i = -4 * e * l, 4 * e - 1, 7/2 - i);
interp(e, l, c, q, swap, ex, ec, dmax) = {
  my(xs = vector(dmax + 3, i, Mod(i + 1, q)));
  my(ys = parvector(dmax + 3, i, Dval(e, l, c, lift(xs[i]), q, swap) * xs[i]^ex * (1 + c * xs[i])^ec));
  my(P = polinterpolate(xs[1..dmax + 1], ys[1..dmax + 1], 'x));
  if (subst(P, 'x, xs[dmax + 2]) != ys[dmax + 2] || subst(P, 'x, xs[dmax + 3]) != ys[dmax + 3], return(0));
  P;
}
\\ G_X exactly (as in the _g script)
ser(a, gs, Ds, P) = { my(f = 'u^a * prod(i = 1, #gs, (1 + 'u / Ds[i] + O('u^(P + 1)))^gs[i])); vector(P + 1, m, polcoef(f, m - 1, 'u)); }
tri(rows, piv, col) = { my(A = matrix(#rows, #rows[1], i, j, rows[i][j]), S = matrix(#rows, #piv, i, j, A[i, piv[j]]), B = S^(-1) * A); B[#piv, col]; }
Gvec(e, l, D) = {
  my(Rl = Rn(l), P = Rl + 4 * e * l + 8, rA = List(), rB = List(), rC = List());
  for (s = 1, l, listput(rA, ser(3, [-3], [D[s]], P)));
  for (r = 1, l, for (s = r + 1, l, for (j = 0, 3, listput(rA, ser(6 - j, [-5/2, -7/2], [D[r], D[s]], P)))));
  for (s = 1, l, for (j = 0, 4 * e - 1, listput(rB, ser(j, [-7/2], [D[s]], P))));
  for (s = 1, l, for (j = 0, 3, listput(rC, ser(j, [-7/2], [D[s]], P))));
  [tri(rA, vector(Rl, i, i + 3), Rl + 4), tri(rB, vector(4 * e * l, i, i), 4 * e * l + 1), tri(rC, vector(4 * l, i, i), 4 * l + 1)];
}
main() = {
  my(q = 2^61 - 1, CS = [2, -3, 5, -7, 11, -13, 17, -19], st = if (getenv("ST"), eval(getenv("ST")), 12));
  foreach ([[4, 3], [5, 4], [4, 2], [5, 3], [5, 2]], bp,
    my(b = bp[1], p = bp[2], e = p - 1, l = b - p, c = CS[p], N = 2 * b, R = Rn(b), B = binomial(R, 2), Sc = md(N, 7/2));
    my(w0 = sum0(e, l) - B, wc = Sc - B, nF = B - Sc - sum0(e, l) - sumatinf(e, l));
    my(Sb = sum(k = 1, 6, blocks(e, l)[k][2] * blocks(e, l)[k][3]), Sg = sum(k = 1, 6, blocks(e, l)[k][1] * blocks(e, l)[k][3]));
    my(A0 = Sb - w0, Ac = Sg - wc);
    my(W = interp(e, l, c, q, 0, A0, Ac, nF));
    if (W == 0 || poldegree(W) != nF, error("W"));
    my(PX = vector(3), idx = [3, 6, 5], line = Str("(b,k)=", bp, " (e,l)=(", e, ",", l, ") deg W ", nF, ":"), ok = 1);
    for (t = 1, 3, PX[t] = interp(e, l, c, q, idx[t], A0 - 1 + st, Ac + st, nF + 3 * st + 4);
      if (PX[t] == 0, ok = 0; line = Str(line, " P_", ["A", "B", "C"][t], " interpolation failed;")));
    if (!ok, emit(line); next);
    my(D = vector(l, s, [2, 5, 11, 17][s] / 3), G = Gvec(e, l, D), Gq = apply(g -> Mod(numerator(g), q) / Mod(denominator(g), q), G));
    my(Wm = Mod(W, W), U = Mod('x^st * (1 + c * 'x)^st * deriv(W), W), Ui = U^(-1));
    my(SX = vector(3, t, lift(Mod(PX[t], W) * Ui)));
    my(S = lift(sum(t = 1, 3, Gq[t] * Mod(PX[t], W)) * Ui));
    line = Str(line, " deg(Q_X/W' mod W) for A, B, C: ", apply(poldegree, SX), "; deg(R_1/W' mod W) at D = (2,5,11,17)/3: ", poldegree(S),
      if (poldegree(S) <= 2, " (MOEBIUS: R_1 = v W' mod W, deg v <= 2)", " (not Moebius)"));
    emit(line));
}
default(nbthreads, 12);
default(parisizemax, 2000000000);
main();
