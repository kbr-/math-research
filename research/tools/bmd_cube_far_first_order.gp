\\ First-order correction of the far Wronskian in the even peeling (3 October 2026; cycle bmd-20261003-zd).
\\ Near the far limit (x = eps z, D_k = eps c) the classes of E_(k-1) that depend on the other doubles D_s (s > k) are
\\   A: V^(l) at scale 1/eps, limit x^-(R_l+2) P_<R_l;   B: extension blocks of s > k, limit x^(-7/2+4e-4el) P_<4el;
\\   C: pairs (k,s), limit (1+cx)^-5/2 x^(1/2-4l) P_<4l.
\\ In each class the triangular basis at the cluster (w = eps/x) has its first correction on the element of highest w-order
\\ (the most negative power of x), at relative order eps^1: x^a -> x^a + G_X(D) eps x^(a-1).  So the eps^1 term of the far
\\ Wronskian is sum_X G_X(D) W(F_k with that element replaced by x^(a-1)) =: sum_X G_X(D) Q_X (same normalization as W_k).
\\ Question: do Q_A, Q_B, Q_C have common roots with W_k, with each other, or a structural relation to W_k?
\\ A triple root r of W_k splits into simple points if sum_X G_X(D) Q_X(r) != 0.  Computed modulo q = 2^61 - 1 at the
\\ c of the far-components script, by evaluation at points and interpolation with two extra checks.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
blocks(e, l) = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Rn(l) + 2), Rn(l)], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]];
rowf(ga, be, j, c, x0, R, q) = {
  my(u = vector(R, a, Mod(binomial(be + j, a - 1), q) * x0^(j - a + 1)), r = Mod(c, q) / (1 + c * x0));
  my(v = vector(R, s, Mod(binomial(ga, s - 1), q) * r^(s - 1)));
  vector(R, m, sum(a = 1, m, u[a] * v[m + 1 - a]));
}
\\ swap = 0 (none) or the index of the block (3 = A, 6 = B, 5 = C) whose j = 0 element gets exponent - 1
Dval(e, l, c, x0, q, swap) = {
  my(R = Rn(e + l + 1), rows = List(), bl = blocks(e, l));
  for (k = 1, #bl, for (j = 0, bl[k][3] - 1, listput(rows, rowf(bl[k][1], bl[k][2] - (k == swap && j == 0), j, c, x0, R, q))));
  matdet(Mat(Vec(rows)~));
}
\\ normalized polynomial: D(x0) x0^A0 (1 + c x0)^Ac with A0, Ac the exponent-sum corrections (as in the far script),
\\ times x0^sh; interpolated with degree bound dmax and two extra checks
poly(e, l, c, q, swap, A0, Ac, sh, dmax) = {
  my(xs = vector(dmax + 3, i, Mod(i + 1, q)));
  my(ys = parvector(dmax + 3, i, Dval(e, l, c, lift(xs[i]), q, swap) * xs[i]^(A0 + sh) * (1 + c * xs[i])^Ac));
  if (#select(y -> y != 0, ys) == 0, return("ZERO"));
  my(P = polinterpolate(xs[1..dmax + 1], ys[1..dmax + 1], 'x));
  if (subst(P, 'x, xs[dmax + 2]) != ys[dmax + 2] || subst(P, 'x, xs[dmax + 3]) != ys[dmax + 3], return(0));
  P;
}
export(Rn, blocks, rowf, Dval);
md(N, c) = my(K = 2 * N - 4); -c * K + binomial(K, 2) - 3 + binomial(binomial(N - 2, 2), 2);
sum0(e, l) = -sum(j = 3, Rn(l) + 2, j) + sum(j = 0, Rn(e) + 4 * e, j) + sum(i = 4 * e - 4 * e * l, 4 * e + 4 * l - 1, i - 7/2);
sumatinf(e, l) = -binomial(Rn(e), 2) + sum(j = 3, Rn(l) + 4 * l + 3, j) + sum(i = -4 * e * l, 4 * e - 1, 7/2 - i);
main() = {
  my(q = 2^61 - 1, CS = [2, -3, 5, -7, 11, -13, 17, -19]);
  foreach ([[4, 2], [4, 3], [5, 2], [5, 3], [5, 4]], bp,
    my(b = bp[1], p = bp[2], e = p - 1, l = b - p, c = CS[p], N = 2 * b, R = Rn(b), B = binomial(R, 2), Sc = md(N, 7/2));
    my(w0 = sum0(e, l) - B, wc = Sc - B, nF = B - Sc - sum0(e, l) - sumatinf(e, l));
    my(Sb = sum(k = 1, 6, blocks(e, l)[k][2] * blocks(e, l)[k][3]), Sg = sum(k = 1, 6, blocks(e, l)[k][1] * blocks(e, l)[k][3]));
    my(A0 = Sb - w0, Ac = Sg - wc);
    my(W = poly(e, l, c, q, 0, A0, Ac, 0, nF));
    if (W == 0 || poldegree(W) != nF, error("W"));
    my(Q = vector(3), names = ["A", "C", "B"], idx = [3, 5, 6], line = Str("(b,k)=", bp, " (e,l)=(", e, ",", l, ") deg W ", nF, ":"));
    for (t = 1, 3,
      \\ the swap lowers the exponent sum at 0 by one; shift by x^1 and allow a few extra degrees
      Q[t] = poly(e, l, c, q, idx[t], A0, Ac + 40, 40, nF + 120); if (type(Q[t]) == "t_POL", Q[t] = Q[t] / 'x^valuation(Q[t], 'x); while (subst(Q[t], 'x, Mod(-1, q) / c) == 0, Q[t] = Q[t] / (1 + c * 'x)));
      if (Q[t] === "ZERO", line = Str(line, " Q_", names[t], " identically 0;"); Q[t] = 0; next);
      if (Q[t] == 0, line = Str(line, " Q_", names[t], " interpolation FAILED;"); next);
      my(g = gcd(W, Q[t]));
      line = Str(line, " Q_", names[t], ": deg ", poldegree(Q[t]), ", val_x ", valuation(Q[t], 'x), ", deg gcd(W,Q) ", poldegree(g), ";"));
    my(g3 = gcd(gcd(Q[1], Q[2]), Q[3]), gW = gcd(W, g3));
    my(M = matrix(3, nF + 121, i, j, polcoef(Q[i], j - 1)), rk = matrank(M));
    line = Str(line, " deg gcd(Q_A,Q_B,Q_C) ", poldegree(g3), ", with W ", poldegree(gW), "; rank of (Q_A,Q_B,Q_C) ", rk);
    \\ structural test: is some combination of the Q_X in the span of W, x W, W' (a relation that would vanish at multiple roots)?
    my(S = [W, 'x * W, deriv(W), 'x * deriv(W), 'x^2 * deriv(W)], MM = matrix(3 + #S, nF + 121, i, j, polcoef(if (i <= 3, Q[i], S[i - 3]), j - 1)));
    line = Str(line, "; rank with W, xW, W', xW', x^2W' ", matrank(MM), " of ", 3 + #S);
    emit(line));
}
default(nbthreads, 12);
default(parisizemax, 2000000000);
main();
