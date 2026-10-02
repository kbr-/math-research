\\ Cherry cross block in the basis w^(-lambda+t), w = 1+T (7 October 2026; cycle bmd-20261007-t).
\\ lambda = 3/2.  The cross rows of the cherry join x*D ∪ {1, 1+e} are, up to constants and the factor w^(-lambda),
\\ V_s = (1 + b_s w)^(-lambda) and Q_s = ((1 + eps/w)^(-lambda) - 1) V_s, with b_s = x*y_s (b_s and eps are the
\\ reparametrized roots b/(1-b) and (1-a)/a; their leading terms are those of x*y_s and -e).  The coefficient of w^t
\\ is c_t b^t in V_s and sum_{r >= max(1,-t)} c_r c_(t+r) eps^r b^(t+r) in Q_s, with c_n = binomial(-lambda, n).
\\ For each M and window Lambda_j = [-j, 2M-1-j] (1 <= j <= M), the Plucker coordinate on Lambda_j is computed with
\\ the entries truncated at eps-degree B = j^2 - j + M (exact for every coefficient of eps-degree <= B).  It prints
\\ (1) whether every coefficient of x^a eps^b with a + b < A + B, or with a < A, or with b < B, vanishes, where
\\ A = 2M^2 - 2Mj + j^2 - j is the predicted x-degree, and (2) the coefficient L_j = [x^A eps^B] divided by
\\ Vand(y)^2, factored.  Symbolic y for M <= MS, random integer y for larger M (nonvanishing only).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
MS = 3; MMAX = 4;
{
for (M = 2, MMAX,
  my(ys = if (M <= MS, vector(M, s, eval(Str("y", s))), vector(M, s, random(97) + 1)));
  my(vd = prod(s = 1, M, prod(t = s + 1, M, ys[t] - ys[s])));
  for (j = 1, M,
    my(A = 2*M^2 - 2*M*j + j^2 - j, B = j^2 - j + M, L = vector(2*M, u, u - 1 - j), G = matrix(2*M, 2*M));
    for (s = 1, M,
      for (u = 1, 2*M, my(t = L[u]);
        G[s, u] = if (t >= 0, cc(t) * (x * ys[s])^t, 0);
        G[M + s, u] = sum(r = max(1, -t), B, cc(r) * cc(t + r) * eps^r * (x * ys[s])^(t + r))));
    my(P = matdet(G), ok = 1, lead);
    \\ lower-order coefficients: total degree below A + B, or x-degree below A, or eps-degree below B
    for (b = 0, B, my(pb = polcoef(P, b, eps));
      for (a = 0, A + B, my(pab = polcoef(pb, a, x));
        if (pab != 0 && (a + b < A + B || a < A || b < B), ok = 0)));
    lead = polcoef(polcoef(P, B, eps), A, x);
    emit(Str("M = ", M, ", j = ", j, ": A = ", A, ", B = ", B, ", no lower terms: ", ok,
      ", L_j / Vand^2 = ", if (M <= MS, factor(lead / vd^2), lead / vd^2)))));
}
