\\ Appell lead (cycle ken, 9 October 2026): the weighted pair-row sequence of lem:cube-level-window-reduction.
\\ For a pair row e = coefficients of ((1+aT)(1+bT))^(-3/2) and rho_k = k!/Gamma(k+5/2-m), c_k = rho_k e_k satisfies
\\   c_(k+1) = -(a+b)(k+3/2)/(k+5/2-m) c_k - ab k(k+2)/((k+5/2-m)(k+3/2-m)) c_(k-1)     (k >= 1),
\\ from (k+1)e_(k+1) = -(a+b)(k+3/2)e_k - ab(k+2)e_(k-1).  Exact check for m = 2..6, k < 60, at three (a,b) pairs.
\\ rho_k is computed up to the common factor 1/sqrt(pi) (Gamma at half-integers), which cancels in the recurrence.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
G(x) = if(x == 1/2, 1, if(x > 1/2, (x - 1) * G(x - 1), G(x + 1) / x));   \\ Gamma(x)/sqrt(pi) at half-integers
{
  my(bad = 0, tot = 0);
  foreach([[2, 5], [-3, 7/2], [1/3, -4]], ab, my(a = ab[1], b = ab[2], s = ((1 + a * 'T) * (1 + b * 'T) + O('T^62))^(-3/2));
    for(m = 2, 6,
      my(c = vector(61, k, (k - 1)! / G(k - 1 + 5/2 - m) * polcoef(s, k - 1, 'T)));
      for(k = 1, 59, tot++;
        my(rhs = -(a + b) * (k + 3/2) / (k + 5/2 - m) * c[k + 1] - a * b * k * (k + 2) / ((k + 5/2 - m) * (k + 3/2 - m)) * c[k]);
        if(c[k + 2] != rhs, bad++))));
  emit(Str("three-term recurrence for c_k = rho_k e_k: ", tot - bad, " of ", tot, " identities hold (m = 2..6, k = 1..59, three (a,b))"));
}
quit;
