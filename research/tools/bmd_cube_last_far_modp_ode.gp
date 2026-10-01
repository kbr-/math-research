\\ Igusa-type test for the non-branch factor modulo window primes (3 October 2026; cycle bmd-20261003-zr).
\\ For W = W_(b-1) (saved, e = 2, 3) and each window prime max(d, 2n) < p <= 2n+8e+7 (prop:cube-last-far-eisenstein-branch),
\\ let G_p = W mod p with the factors x and 1+x removed.  Question: does G_p (or W mod p) satisfy a linear ODE over F_p of
\\ order r <= 3 of three-point Fuchsian shape, sum_k (x(1+x))^k c_k(x) D^k, deg c_k <= r - k + s (s = slack allowing apparent
\\ singularities)?  Such an ODE with c_r coprime to G_p excludes roots of multiplicity in [r, p) of G_p (Taylor recurrence),
\\ as in Igusa's proof that Hasse polynomials are squarefree.  Reports the kernel dimension for r = 1..4, s = 0..2, and whether
\\ some kernel vector has top coefficient coprime to G_p.  Control: an ODE count with more unknowns than equations is flagged.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
odetest(P, p, r, s) = {
  my(cols = List(), N = poldegree(P) + 2 * r + s + 2);
  for (k = 0, r, my(Pk = P); for (i = 1, k, Pk = deriv(Pk, 'x)); my(B = ('x * (1 + 'x))^k * Pk);
    for (j = 0, r - k + s, listput(cols, [k, j, B * 'x^j])));
  my(M = matrix(N, #cols, i, c, polcoef(cols[c][3], i - 1, 'x)) * Mod(1, p), K = matker(M));
  my(good = 0);
  for (c = 1, #K, my(v = K[, c], top = sum(i = 1, #cols, if (cols[i][1] == r, v[i] * 'x^cols[i][2], 0)));
    if (top != 0 && poldegree(gcd(lift(top) * Mod(1, p), P)) == 0, good = 1));
  [#K, #cols, N, good];
}
{
for (e = 2, 3,
  my(W = read(Str("research/results/bmd-20261003-zl/W_last_e", e, ".gp")), n = Rn(e), d = Rn(e + 2));
  forprime (p = max(d, 2 * n) + 1, 2 * n + 8 * e + 7,
    my(Wp = W * Mod(1, p), G = Wp);
    while (subst(G, 'x, 0) == 0, G /= 'x); while (subst(G, 'x, -1) == 0, G /= (1 + 'x));
    emit(Str("e=", e, " p=", p, ": deg G_p = ", poldegree(G)));
    foreach ([["G_p", G], ["W mod p", Wp]], T,
      for (r = 1, 4, for (s = 0, 2, my(t = odetest(T[2], p, r, s));
        if (t[1] > 0 || (r == 3 && s == 0), emit(Str("  ", T[1], " r=", r, " s=", s, ": kernel ", t[1], " (unknowns ", t[2], ", equations ", t[3], ")",
          if (t[2] > t[3], " [underdetermined]", ""), if (t[4], " top coprime to G", "")))))))));
}
