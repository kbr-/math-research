\\ Pair Wronskian of the integral class of the last-step six-space (3 October 2026; cycle bmd-20261003-zv).
\\ By prop:cube-last-far-six-space, U = <u_1, u_2> with u_1 = t^(n+k+3) P_k^(n+7/2,-k-3/2)(1-2t) and
\\ u_2 = t^(k-1/2)(1-t)^(k+3/2) d_t^k[t^(1/2)(1-t)^(-3/2) P_k^(-n-k-3,-3/2)(1-2t)].  Its Wronskian has exactly 8e = 2k zeros
\\ off t in {0,1} (lem:cube-last-far-reduction count).  Question: is that far part G_U a Gauss hypergeometric polynomial, i.e.
\\ does it satisfy t(1-t) y'' + (c - (A+B+1) t) y' - A B y = 0 for some constants (A, B, c)?  Linear in (c, A+B+1, AB): solve
\\ by least squares over Q and test exactness.  Also: real-root count, and whether G_U is irreducible over Q.  e = 1, 2, 3.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
dt(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 - 't) * p - g * 't * p + 't * (1 - 't) * deriv(p, 't)];
jacobi(k, al, be) = my(z = 1 - 2 * 't); sum(s = 0, k, binomial(k + al, k - s) * binomial(k + be, s) * ((z - 1) / 2)^s * ((z + 1) / 2)^(k - s));
far(P) = { P /= 't^valuation(P, 't); while (subst(P, 't, 1) == 0, P /= (1 - 't)); P; }
{
for (e = 1, 3,
  my(n = Rn(e), k = 4 * e, u1 = 't^(n + k + 3) * jacobi(k, n + 7/2, -k - 3/2), f = [1/2, -3/2, jacobi(k, -n - k - 3, -3/2)]);
  for (r = 1, k, f = dt(f));
  \\ f = t^(1/2-k) (1-t)^(-3/2-k) p; u_2 = t^(k-1/2) (1-t)^(k+3/2) f = p
  if (f[1] != 1/2 - k || f[2] != -3/2 - k, error("unexpected exponents"));
  my(u2 = f[3], G = far(u1 * deriv(u2, 't) - deriv(u1, 't) * u2));
  my(y = G, cols = [deriv(y, 't), -'t * deriv(y, 't), -y], rhs = -'t * (1 - 't) * deriv(deriv(y, 't), 't), N = poldegree(G) + 3);
  my(M = matrix(N, 3, i, j, polcoef(cols[j], i - 1, 't)), v = vectorv(N, i, polcoef(rhs, i - 1, 't)), r = matrank(M), r2 = matrank(concat(M, v)));
  emit(Str("e=", e, ": deg u_2 = ", poldegree(u2), ", far degree of W(u_1, u_2) = ", poldegree(G), " (2k = ", 2 * k, ")",
    ", hypergeometric equation: ", if (r == r2, "YES", "no"), ", real roots ", #polrootsreal(G), ", irreducible ", polisirreducible(G))));
}
