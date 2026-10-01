\\ Pair-collision induction test (5 October 2026; cycle bmd-20261005-d).  Hypothesis: in characteristic 3 the leading
\\ eps-coefficient of Delta_(n,2) at a pair collision a_N = a_(N-1) + eps is divisible by Delta_(n-1,2) of the first N-1
\\ labels, so nonvanishing would propagate from n-1 to n.  Labels a_1 = 0 (dummy), a_k = t^(k-1) for 2 <= k <= N-1 over
\\ F_3(t), a_N = a_(N-1) + eps.  Output: eps-order, factorization of the leading coefficient L, of Delta_(N-1 labels), and
\\ the largest power of the latter dividing L.  Env NS (list of N), PRIME (default 3).
default(parisizemax, 4000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
mark(lab, one) = {
  my(N = #lab, D = N * (N - 1) / 2 + 2, bh = vector(D, j, binomial(1/2, j - 1) * one), M = matrix(D, D), row = 2);
  M[1, 1] = one; M[2, 2] = one;
  for (i = 1, N, for (j = i + 1, N, row++;
    for (kk = 1, D, M[row, kk] = sum(u = 0, kk - 1, bh[u + 1] * bh[kk - u] * lab[i]^u * lab[j]^(kk - 1 - u)))));
  matdet(M);
}
{
my(t = 't, e = 'e, pr = if(getenv("PRIME") != "" && getenv("PRIME") != 0, eval(getenv("PRIME")), 3), one = Mod(1, pr));
foreach(eval(getenv("NS")), N,
  my(base = vector(N - 1, k, if(k == 1, 0 * one, t^(k - 1) * one)), t0 = getwalltime());
  my(dl = mark(concat(base, [base[N - 1] + e * one]), one));
  if (dl == 0, emit(Str("N = ", N, ": Delta = 0 identically")); next);
  my(v = valuation(dl, e), L = polcoef(dl, v, e), d0 = mark(base, one), k = 0, q = L);
  if (d0 == 0, emit(Str("N = ", N, ": Delta of the first N-1 labels vanishes for these labels")); next);
  while (q % d0 == 0, q = q / d0; k++);
  emit(Str("N = ", N, ", p = ", pr, ": eps-order ", v, "; Delta(N-1 labels) = ", factor(d0), "; leading coefficient = ", factor(L),
    "; largest power of Delta(N-1 labels) dividing it: ", k, " (", getwalltime() - t0, " ms)")));
}
quit;
