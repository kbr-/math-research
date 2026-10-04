\\ Symmetric form of the triple window (cycle bmd-20261009-kga, 9 October 2026; prop:cube-triple-window-symmetric-factorization).
\\ Row k of the reduced triple window U_3(a) is R_n(a_k), R_n(z) = sum_l binom(m,l) z^l rho_(n-l) g_(n-l)(z), where g_r is the
\\ coefficient of T^r in (1 + (e1 - z) T + (e2 - e1 z + z^2) T^2)^(-3/2); reducing R_n modulo f = z^3 - e1 z^2 + e2 z - e3 gives
\\ U_3(a) = W(a) C(e(a)) with W the Vandermonde matrix (a_k^i) and C the 3 x 5 matrix of residue coefficients.
\\ Modes (env MODE):
\\   check : at M, compares every maximal minor of the window as exported in the chart a = (u, v, 1) with V * det C_S(e(u, v, 1)),
\\           V = (u - v)(u - 1)(v - 1), and prints whether one sign fits all ten minors (the factorization's control).
\\   A     : writes OUT/sym-A-mM.ms, msolve input in e2, e3, t for chart e1 = 1: the ten minors det C_S(1, e2, e3) (contents cleared)
\\           and the Rabinowitsch generator t e3 Delta(1, e2, e3) - 1; with NEG=2 only the first two minors (a negative control,
\\           which must have common zeros). Also prints chart B: the degree of gcd_S det C_S(0, e2, 1) after removing the factors
\\           of Delta(0, e2, 1) = -4 e2^3 - 27 (zero means no common root in chart B).
\\ Usage: env MODE=A M=11 OUT=dir gp -q bmd_triple_window_symmetric_export.gp
default(parisizemax, 4 * 10^9);
lam = 3/2;
rq(j, k) = prod(i = 1, k, i / (i + lam - j));
\\ rational content only: PARI's content() of a polynomial over Q[c] is a polynomial gcd, and dividing by it could drop zeros
qcontent(P) = if (type(P) == "t_POL", my(g = 0); for (i = 0, poldegree(P), g = gcd(g, qcontent(polcoef(P, i)))); g, P);
cc(n) = binomial(-lam, n);
det3(A) = A[1,1] * (A[2,2] * A[3,3] - A[2,3] * A[3,2]) - A[1,2] * (A[2,1] * A[3,3] - A[2,3] * A[3,1]) + A[1,3] * (A[2,1] * A[3,2] - A[2,2] * A[3,1]);
disc(e1, e2, e3) = e1^2 * e2^2 - 4 * e2^3 - 4 * e1^3 * e3 + 18 * e1 * e2 * e3 - 27 * e3^2;
\\ The residue matrix C (3 x 5) over the coefficient ring of e1, e2, e3 (z is the main variable 'x).
residues(m, e1, e2, e3) = {
  my(N0 = m * (m + 1) / 2, top = N0 + 4, f = 'x^3 - e1 * 'x^2 + e2 * 'x - e3, z = Mod('x, f), s = e1 - z, p = e2 - e1 * z + z^2);
  my(g = vector(top + 1)); g[1] = Mod(1, f);
  for (r = 1, top, g[r + 1] = -(s * (r - 1 + lam) * g[r] + if (r >= 2, p * (r - 2 + 2 * lam) * g[r - 1], 0)) / r);
  my(C = matrix(3, 5));
  for (col = 1, 5, my(n = N0 + col - 1, R = sum(l = 0, m, if (n - l >= 0, binomial(m, l) * z^l * rq(-m, n - l) * g[n - l + 1], 0)));
    my(L = lift(R)); for (i = 0, 2, C[i + 1, col] = polcoef(L, i, 'x)));
  C;
}
\\ The window as exported (research/tools/bmd_triple_window_export_m.gp), rows (12|3), (13|2), (23|1), in the chart a = (u, v, 1).
oldwindow(m) = {
  my(a = ['u, 'v, 1], N0 = m * (m + 1) / 2, U = matrix(3, 5), prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
  for (r = 1, 3, my([i, j, k] = prs[r], top = N0 + 4);
    my(e = vector(top + 1, n, sum(t = 0, n - 1, cc(t) * cc(n - 1 - t) * a[i]^t * a[j]^(n - 1 - t))));
    for (col = 1, 5, my(n = N0 + col - 1);
      U[r, col] = sum(l = 0, m, binomial(m, l) * a[k]^l * if (n - l >= 0, rq(-m, n - l) * e[n - l + 1], 0))));
  U;
}
{
  my(mode = getenv("MODE"), m = eval(getenv("M")));
  if (mode == "check",
    my(U = oldwindow(m), C = residues(m, 'a, 'b, 'c), V = ('u - 'v) * ('u - 1) * ('v - 1), signs = List(), conts = List());
    forsubset([5, 3], S, my(Sv = Vec(S));
      my(D = det3(matrix(3, 3, r, t, U[r, Sv[t]])), G = substvec(det3(matrix(3, 3, r, t, C[r, Sv[t]])), ['a, 'b, 'c], ['u + 'v + 1, 'u * 'v + 'u + 'v, 'u * 'v]));
      listput(signs, if (D == V * G, 1, if (D == -V * G, -1, 0))); listput(conts, content(D) / qcontent(D)));
    print("check m = ", m, ": old non-numeric contents ", Set(Vec(conts)), ", signs ", Vec(signs), if (#Set(Vec(signs)) == 1 && signs[1] != 0, " (factorization holds)", " (FAILS)"));
    quit);
  my(outdir = getenv("OUT"), neg = getenv("NEG"), nmin = if (neg == 0 || neg == "", 10, eval(neg)));
  my(C = residues(m, 1, 'b, 'c), gens = List());
  forsubset([5, 3], S, my(Sv = Vec(S), D = det3(matrix(3, 3, r, t, C[r, Sv[t]]))); if (D != 0, listput(gens, D / qcontent(D))));
  my(G = Str(outdir, "/sym-A-m", m, if (nmin < 10, Str("-neg", nmin), ""), ".ms"));
  write(G, "b,c,t"); write(G, "0");
  for (g = 1, min(nmin, #gens), write(G, gens[g], ","));
  write(G, "t*c*(", disc(1, 'b, 'c), ")-1");
  my(degs = vector(#gens, g, my(P = gens[g]); vecmax(vector(poldegree(P, 'b) + 1, i, my(q = polcoef(P, i - 1, 'b)); if (q == 0, -1, i - 1 + poldegree(q, 'c))))));
  my(CB = residues(m, 0, 'b, 1), h = 0);
  forsubset([5, 3], S, my(Sv = Vec(S)); h = gcd(h, det3(matrix(3, 3, r, t, CB[r, Sv[t]]))));
  my(d = -4 * 'b^3 - 27, q); while (poldegree(q = gcd(h, d)) > 0, h = h / q);
  print("m = ", m, ": chart A, ", min(nmin, #gens), " minors, total degrees ", degs, "; chart B, residual gcd degree ", poldegree(h));
  quit;
}
