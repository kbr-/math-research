\\ Far polynomials modulo primes (3 October 2026; cycle bmd-20261003-l)
\\ Question: R_(n,k) in Q[w] (lem:cube-far-u-space; construction of research/tools/bmd_cube_far_u_space.gp) is squarefree
\\ over Q if its reduction mod one prime p keeps the degree and is squarefree.  For which p does that happen, and is
\\ there a prime, depending on (n,k), at which R mod p splits into linear factors (an explicit product, a candidate for
\\ an all-(n,k) proof)?  For each (n,k) and each odd prime p < PMAX not dividing a denominator: degree kept?
\\ squarefree?  factorization degree pattern.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
stripw(N) = { while (subst(N, 'w, 0) == 0, N = N / 'w); while (subst(N, 'w, 1) == 0, N = N / ('w - 1)); N; }
wr(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  stripw(numerator(matdet(M)));
}
far(n, k) = {
  my(hh = 1/2, C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, hh - (n - 1) + t - 1)), q = #E);
  my(P3 = vector(k - 1, j, my(p = 'w^(j - 1), al = hh); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); p));
  my(P4 = vector(n, j, my(p = 'w^(j - 1), al = hh); for (i = 1, q, p = thetastep(p, al, hh - (n - 1), E[i]); al--); p));
  my(R = wr([[0, 0, P3], [hh, 0, apply(p -> p * 'w^(-(n - 1)), P4)]]));
  R = R / content(R); R;
}
main() = {
  my(cases = eval(getenv("CASES")), PMAX = eval(getenv("PMAX")));
  foreach(cases, v, my(R = far(v[1], v[2]), d = poldegree(R), good = List(), split = List());
    emit(Str("(n,k)=", v, ": deg R = ", d, ", squarefree over Q: ", poldisc(R) != 0, ", factor degrees over Q: ", apply(poldegree, factor(R)[, 1]~)));
    forprime(p = 3, PMAX, my(Rp = R * Mod(1, p));
      if (poldegree(lift(Rp)) < d, next);
      if (poldisc(Rp) == 0, next);
      listput(good, p);
      my(F = factormod(lift(Rp), p)[, 1]~);
      if (vecmax(apply(poldegree, F)) == 1, listput(split, p)));
    emit(Str("  primes < ", PMAX, " with degree kept and squarefree: ", #good, " (first: ", Vec(good)[1..min(12, #good)], ")"));
    emit(Str("  of those, primes where R mod p splits into distinct linear factors: ", Vec(split))));
}
default(parisizemax, 2000000000);
main();
quit
