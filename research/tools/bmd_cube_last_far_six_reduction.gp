\\ Six-function reduction check (3 October 2026; cycle bmd-20261003-zt).
\\ Claim: A' = P_<n + (1+x)^(-7/2) P_<4e + x^(-7/2) P_<4e (n = R_e) has Wronskian c x^a (1+x)^b (no zeros off 0, -1), so
\\ by the Polya-Mammana factorization W(F_(b-1)) = W(A') W(L_A' B') with B' = <(1+x)^-3, x^-3> + (1+x)^(-5/2) x^(-7/2) P_<4,
\\ and W_(b-1) is the far part of the Wronskian of the six functions L_A'(B').
\\ Check (mod q = 2^61 - 1, e = 1..4): det of the h-matrix of A' (as in bmd_cube_last_far_kappa.gp: f = x^b (1+x)^g p,
\\ f^(m) = x^(b-m) (1+x)^(g-m) h_m) is a monomial times a power of 1+x; and, control, the same for A = A' + <(1+x)^-3, x^-3>
\\ (recorded: exactly 8e far zeros).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
Rn(n) = n * (2 * n - 1);
detH(bl) = {
  my(d = sum(i = 1, #bl, bl[i][3]), M = matrix(d, d), row = 0);
  foreach (bl, B, my(g = B[1], b = B[2]); for (j = 0, B[3] - 1, row++; my(h = Mod(1, q) * 'x^j);
    for (m = 0, d - 1, M[row, m + 1] = h; h = 'x * (1 + 'x) * deriv(h, 'x) + (b * (1 + 'x) + g * 'x - m * (1 + 2 * 'x)) * h)));
  matdet(M);
}
farpart(P) = { my(a = valuation(lift(P), 'x)); P /= 'x^a; while (subst(P, 'x, -1) == 0, P /= (1 + 'x)); poldegree(P); }
default(parisizemax, 4000000000);
{
for (e = 1, 3,
  my(n = Rn(e), Ap = [[0, 0, n], [-7/2, 0, 4 * e], [0, -7/2, 4 * e]], A = concat(Ap, [[-3, 0, 1], [0, -3, 1]]), IV = [-5/2, -7/2, 4]);
  emit(Str("e=", e, ": far degree of W(A') = ", farpart(detH(Ap)), " (claim 0); control W(A' + class integrals) = ", farpart(detH(A)), " (recorded 8e = ", 8 * e, ")"));
  \\ further splittings: far degrees of W(A' + S) for sub-blocks S of B'
  emit(Str("  far degree of W(A' + IV) = ", farpart(detH(concat(Ap, [IV]))), ", W(A' + (1+x)^-3) = ", farpart(detH(concat(Ap, [[-3, 0, 1]]))),
    ", W(A' + x^-3) = ", farpart(detH(concat(Ap, [[0, -3, 1]]))), ", W(A' + (1+x)^-3 + IV) = ", farpart(detH(concat(Ap, [[-3, 0, 1], IV]))), ", W(A' + x^-3 + IV) = ", farpart(detH(concat(Ap, [[0, -3, 1], IV]))),
    ", full W(F) = ", farpart(detH(concat(A, [IV]))))));
}
