\\ Weierstrass points of the binary-face limit space.
\\
\\ Tested statement: for the cluster degeneration (eps*b_1,...,eps*b_M, s, t) of the degree-two
\\ pair space, the limit space is (after an affine change of T putting the branch values at -1, 1)
\\   Phi0 = < T^m (m < r), T^m (1+T)^(-3/2), T^m (1-T)^(-3/2) (m < M), ((1+T)(1-T))^(-3/2) >,
\\ r = binom(M,2), of dimension R = binom(M+2,2). (The naive confluent analogue with rows
\\ T^(m+1)(1+T)^(-5/2) is dependent: its half-integral rows span only (1+T)^(-5/2) Pol_(<=M),
\\ so it is not a limit space and is not computed.)
\\ The question: are the finite non-branch Weierstrass points of these spaces simple (squarefree
\\ Wronskian numerator off T = +-1), and what is the numerator? Computed exactly over Q.
\\ A function (1+T)^a (1-T)^b p(T) has k-th derivative (1+T)^(a-k) (1-T)^(b-k) p_k(T) with
\\ p_(k+1) = p_k' (1-T^2) + p_k ((a-k)(1-T) - (b-k)(1+T)); the Wronskian is the product of the
\\ row and column factors times det[p_(r,k)], and W0 = det[p_(r,k)] is a polynomial whose roots
\\ off T = +-1 have multiplicity equal to the Weierstrass weight.
\\ Output: printed and appended to the file named by env OUT.

OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));

wronsk(rows, R) = {
  \\ entries p_(r,k) as polynomials; the determinant is recovered exactly over Q by evaluation
  \\ at deg+1 integer points (deg <= sum of row degree bounds) and interpolation, then checked
  \\ at two further points
  my(P = vector(R, i, vector(R)), dsum = 0);
  for (i = 1, R,
    my(p = rows[i][1], a = rows[i][2], b = rows[i][3]);
    for (k = 0, R - 1,
      P[i][k + 1] = p;
      p = deriv(p, 'T) * (1 - 'T^2) + p * ((a - k) * (1 - 'T) - (b - k) * (1 + 'T))));
  for (i = 1, R, dsum += vecmax(vector(R, k, poldegree(P[i][k]))));
  my(xs = vector(dsum + 3, j, j + 1), ys = vector(dsum + 3, j,
    matdet(matrix(R, R, i, k, subst(P[i][k], 'T, xs[j])))));
  my(W = polinterpolate(xs[1..dsum+1], ys[1..dsum+1], 'T));
  if (subst(W, 'T, xs[dsum+2]) != ys[dsum+2] || subst(W, 'T, xs[dsum+3]) != ys[dsum+3], error("interpolation check failed"));
  W;
}

report(name, M, W) = {
  if (W == 0, emit(Str(name, " M=", M, ": Wronskian vanishes identically")); return(0));
  my(W1 = W, e1 = 0, e2 = 0);
  while (subst(W1, 'T, -1) == 0, W1 = W1 / ('T + 1); e1++);
  while (subst(W1, 'T, 1) == 0, W1 = W1 / ('T - 1); e2++);
  my(f = factor(W1), degs = vector(#f~, i, [poldegree(f[i, 1]), f[i, 2]]));
  my(sqf = (poldegree(gcd(W1, deriv(W1))) == 0));
  emit(Str(name, " M=", M, " N=", M + 2, " R=", binomial(M + 2, 2), " deg W0=", poldegree(W),
    " mult(T=-1)=", e1, " mult(T=1)=", e2, " deg nonbranch=", poldegree(W1),
    " squarefree=", sqf, " factors [deg,mult]=", degs));
  W1;
}

main() = {
for (M = 3, 6,
  my(r = binomial(M, 2), R = binomial(M + 2, 2), rows = List());
  for (m = 0, r - 1, listput(rows, ['T^m, 0, 0]));
  for (m = 0, M - 1, listput(rows, ['T^m, -3/2, 0]); listput(rows, ['T^m, 0, -3/2]));
  listput(rows, [1, -3/2, -3/2]);
  my(A = report("separated", M, wronsk(rows, R)));
  if (A != 0, emit(Str("  nonbranch numerator (monic): ", A / pollead(A)))));
}
main();
