\\ Review test (2 October 2026; cycle bmd-20261002-x): Wronskians of each class of the reduced far space separately.
\\ For each class P3, P4 (common power of w removed): degree of its Wronskian off w = 0, 1, squarefree or not, and real zeros in
\\ (-oo,0), (0,1), (1,oo).  Karlin-Szego-type results would make the Wronskian of a Jacobi class sign-definite on its
\\ orthogonality interval.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
strip(N) = { while (subst(N, 'w, 0) == 0, N = N / 'w); while (subst(N, 'w, 1) == 0, N = N / ('w - 1)); N / pollead(N); }
plainwr(S) = { my(d = #S, M = matrix(d, d)); for (i = 1, d, my(g = S[i]); for (j = 1, d, M[i, j] = g; g = deriv(g, 'w))); strip(matdet(M)); }
info(W) = {
  my(r = if (poldegree(W) > 0, polrootsreal(W), []));
  Str("deg ", poldegree(W), ", squarefree ", poldegree(gcd(W, deriv(W))) == 0, ", real zeros in (-oo,0),(0,1),(1,oo): ",
    [#select(x -> x < 0, r), #select(x -> x > 0 && x < 1, r), #select(x -> x > 1, r)]);
}
run(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)), q = #E);
  my(P3 = vector(k - 1, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); p));
  my(P4 = vector(n, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 1/2 - (n - 1), E[i]); al--); p));
  my(g3 = fold(gcd, P3), g4 = fold(gcd, P4));
  emit(Str("(n,k)=", [n, k], ": W(P3): ", info(plainwr(apply(p -> p / g3, P3))), " | W(P4): ", info(plainwr(apply(p -> p / g4, P4)))));
}
foreach([[2, 3], [2, 4], [3, 3], [2, 5], [3, 4], [4, 3]], v, run(v[1], v[2]));
