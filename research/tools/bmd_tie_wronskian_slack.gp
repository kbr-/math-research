\\ Where the Wronskian slack goes for square-window relations of the tie window (8 October 2026; cycle bmd-20261008-k).
\\ At a root c0 of D_0 (the minor on the first 3m+3 window columns, stripped of c and c - 1) the rows have a relation
\\ G = g1+...+g5 = O(T^(d+3m+3)) (tie exponent count entry): g1 = P (1+T)^(-5/2), g2 = Q (1+c T)^(-3/2),
\\ g3 = alpha (1+T)^(-3), g4 = u (1+T)^(-5/2) (1+cT)^(-3/2), g5 = -L.  Its Wronskian count has slack 2: the
\\ minimal-exponent bound is B = -2.  A special value of the window is a relation with both units of slack at T = 0.
\\ For each irreducible factor f of D_0 (exactly, over Q[x]/f), prints: deg P, Q, u, L against the maxima
\\ (2m-1, m-1, 1, d-1), alpha != 0, ord_0 G - (d+3m+3), and W/prod(phi) = det[M_ij], M_(i,j+1) = M_ij' + rho_i M_ij,
\\ as T^a (1+T)^b (1+cT)^e S(T): a, b, e, deg S, compared with the rigid values for M = 3m+3.  m = 2.
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
rowco(r, m, k, cc) = {
  if (r <= 2 * m, return(bn(-5/2, k - (r - 1))));
  if (r <= 3 * m, my(n = r - 2 * m - 1); return(bn(-3/2, k - n) * cc^max(k - n, 0)));
  if (r == 3 * m + 1, return(bn(-3, k)));
  if (r == 3 * m + 2, return(sum(a = 0, k, bn(-3/2, a) * bn(-3/2, k - a) * cc^(k - a))));
  sum(a = 0, k - 1, bn(-5/2, a) * bn(-3/2, k - 1 - a) * cc^(k - 1 - a));
}
bser(a, cc, K) = sum(k = 0, K - 1, bn(a, k) * cc^k * 'x^k) + O('x^K);
st(q) = { q = q / 'c^valuation(q, 'c); while (subst(q, 'c, 1) == 0, q = q / ('c - 1)); q; }
Srest0(num, cc) = { my(S = num / 'x^valuation(num, 'x)); while (subst(S, 'x, -1) == 0, S = S / ('x + 1)); while (subst(S, 'x, -1 / cc) == 0, S = S / ('x + 1 / cc)); S / pollead(S); }
ordT(f, pt) = { my(k = 0); if (f == 0, return(oo)); while (subst(f, 'x, pt) == 0, f = f / ('x - pt); k++); k; }
{
for (m = 2, 3, my(d = m * (m - 1) / 2, n = 3 * m + 3);
my(D0 = matdet(matrix(n, n, r, j, rowco(r, m, d + j - 1, 'c))), F = factor(st(D0))[, 1]);
for (t = 1, #F, my(f = subst(F[t], 'c, 'y), cc = Mod('y, f), S = matrix(n, n, r, j, rowco(r, m, d + j - 1, cc)), yy);
  yy = matker(matrix(n, n, j, r, S[r, j]))[, 1];   \\ left kernel: y^T S = 0
  my(P = sum(i = 1, 2 * m, yy[i] * 'x^(i - 1)), Q = sum(i = 1, m, yy[2 * m + i] * 'x^(i - 1)), al = yy[3 * m + 1],
     u = yy[3 * m + 2] * (1 + 'x) + yy[3 * m + 3] * 'x);
  my(K = d + n + 6, Fser = P * bser(-5/2, 1, K) + Q * bser(-3/2, cc, K) + al * bser(-3, 1, K) + u * bser(-5/2, 1, K) * bser(-3/2, cc, K));
  my(L = sum(k = 0, d - 1, polcoef(Fser, k, 'x) * 'x^k), G = Fser - L, ordG = valuation(G, 'x));
  my(A = [P, Q, al / (1 + 'x)^3, u, -L], rho = [-5/2 / (1 + 'x), -3/2 * cc / (1 + cc * 'x), 0, -5/2 / (1 + 'x) - 3/2 * cc / (1 + cc * 'x), 0]);
  my(nz = select(i -> A[i] != 0, [1 .. 5]), k = #nz, Mt = matrix(k, k));
  for (i = 1, k, Mt[i, 1] = A[nz[i]]; for (j = 2, k, Mt[i, j] = deriv(Mt[i, j - 1], 'x) + rho[nz[i]] * Mt[i, j - 1]));
  emit(Str("  nonzero terms ", nz));
  my(R = matdet(Mt), num = numerator(R), den = denominator(R));
  emit(Str("  R == 0: ", R == 0, ", deg num ", poldegree(num, 'x), ", deg den ", poldegree(den, 'x), ", type ", type(R)));
  my(Sm = Srest0(num, cc)); emit(Str("  S monic = ", Sm, "; S(0) as an element of Q(c) has norm ", norm(polcoef(Sm, 0, 'x))));
  my(a = valuation(num, 'x) - valuation(den, 'x), b = ordT(num, -1) - ordT(den, -1), e = ordT(num, -1 / cc) - ordT(den, -1 / cc));
  my(Srest = num / 'x^valuation(num, 'x)); while (subst(Srest, 'x, -1) == 0, Srest = Srest / ('x + 1)); while (subst(Srest, 'x, -1 / cc) == 0, Srest = Srest / ('x + 1 / cc));
  emit(Str("m = ", m, ", factor of D_0 of degree ", poldegree(F[t]), ": deg P, Q, u, L = ", [poldegree(lift(P), 'x), poldegree(lift(Q), 'x), poldegree(lift(u), 'x), poldegree(lift(L), 'x)],
    " (max ", [2 * m - 1, m - 1, 1, d - 1], "), alpha != 0: ", al != 0, ", ord_0 G - (d+3m+3) = ", ordG - (d + n),
    "; W/prod phi = T^", a, " (1+T)^", b, " (1+cT)^", e, " S(T), deg S = ", poldegree(Srest, 'x), " (rigid at M = 3m+3: T^", d + 3 * m - 1, " (1+T)^-16 (1+cT)^-9)")));
);}
quit
