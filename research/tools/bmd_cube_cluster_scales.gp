\\ Scales of the Weierstrass points of a separated configuration near the cluster degeneration.
\\
\\ Tested statement: for roots (eps*b_1,...,eps*b_M, 1, -1) (branch values T = -1/(eps*b_i), -1, 1),
\\ the finite non-branch Weierstrass points of the pair space split into r = binom(M,2) points near
\\ the zeros of Q_r (scale 1), the bubble points at scale 1/eps (as many as the non-branch weight of
\\ a generic one-double-root configuration of N = M+2 roots), and the remaining "neck" points.
\\ Question: at which scales |T| ~ eps^(-alpha) do the neck points lie, and are they simple?
\\ Method: exact Wronskian numerator over Q (rows prod_c (1+cT)^e_c p(T), derivative factors
\\ p_(k+1) = p_k' Pi + p_k sum_c (e_c - k) c Pi/(1+cT), Pi = prod_c (1+cT)), determinant by
\\ evaluation at integer points and exact interpolation, branch factors removed exactly, then
\\ roots numerically at high precision. Output: printed and appended to env OUT.

default(realprecision, 400);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));

numer(vals, R) = {
  \\ rows: all pairs i<j of distinct values vals, exponents -3/2 at each
  my(Nv = #vals, Pi = prod(c = 1, Nv, 1 + vals[c] * 'T), rows = List());
  for (i = 1, Nv, for (j = i + 1, Nv, my(e = vector(Nv)); e[i] = -3/2; e[j] = -3/2; listput(rows, e)));
  my(P = vector(R, i, vector(R)), dsum = 0);
  for (i = 1, R,
    my(p = 1, e = rows[i]);
    for (k = 0, R - 1,
      P[i][k + 1] = p;
      p = deriv(p, 'T) * Pi + p * sum(c = 1, Nv, (e[c] - k) * vals[c] * (Pi / (1 + vals[c] * 'T)))));
  for (i = 1, R, dsum += vecmax(vector(R, k, poldegree(P[i][k]))));
  my(xs = vector(dsum + 3, j, j + 1), ys = vector(dsum + 3, j,
    matdet(matrix(R, R, i, k, subst(P[i][k], 'T, xs[j])))));
  my(W = polinterpolate(xs[1..dsum+1], ys[1..dsum+1], 'T));
  if (subst(W, 'T, xs[dsum+2]) != ys[dsum+2] || subst(W, 'T, xs[dsum+3]) != ys[dsum+3], error("interpolation check failed"));
  foreach (vals, c, while (subst(W, 'T, -1/c) == 0, W = W / ('T + 1/c)));
  W;
}

run(M, b, eps) = {
  my(vals = concat(vector(M, i, eps * b[i]), [1, -1]), R = binomial(M + 2, 2));
  my(W = numer(vals, R), sqf = (poldegree(gcd(W, deriv(W))) == 0));
  my(rts = polroots(W), L = log(1 / eps));
  my(alphas = vecsort(vector(#rts, i, log(abs(rts[i])) / L)));
  emit(Str("M=", M, " N=", M + 2, " b=", b, " eps=", eps, " nonbranch degree=", poldegree(W), " squarefree=", sqf));
  emit(Str("  scale exponents alpha = log|T|/log(1/eps), sorted: ", strjoin(apply(x -> strprintf("%.3f", x), alphas), " ")));
  my(small = #select(x -> x < 0.25, alphas), big = #select(x -> x > 0.75, alphas));
  emit(Str("  counts: alpha<0.25: ", small, "  0.25<=alpha<=0.75: ", #alphas - small - big, "  alpha>0.75: ", big));
  \\ neck clusters: roots with 0.25 <= alpha <= 0.75, grouped by |T|, with arguments in units of pi/3
  my(neck = [z | z <- rts, log(abs(z)) / L >= 0.25 && log(abs(z)) / L <= 0.75]);
  neck = vecsort(neck, z -> [round(log(abs(z)) * 100), arg(z)]);
  emit(Str("  neck points (log|T|, arg/(pi/3)): ", strjoin(apply(z -> strprintf("(%.4f, %.4f)", log(abs(z)), arg(z) / (Pi / 3)), neck), " ")));
}

run(3, [1, 2, -3], 1/1000);
run(3, [1, 2, -3], 1/100000);
run(3, [1, 2, -3], 1/10^10);
