\\ Inductive step for the characteristic-three degree-two determinant (cycle bmd-20261009-z, 9 October 2026).
\\ Setting (lem:cube-ternary-one-root-face): beta(m) = [x^m] (1+x)^(1/2) mod 3 = binom(2, m_0) prod_{j>=1} binom(1, m_j)
\\ (Lucas, 1/2 = ...1112 in base 3); A = {m : beta(m) != 0}; E_n = the n smallest elements of A;
\\ top_n = {binom(n,2)+2, ..., binom(n+1,2)+1}. The strict top term of the Laplace expansion along the rows
\\ containing a_1 is nonzero iff B_n = det[ beta(k - e) ]_{k in top_n, e in E_n} != 0 mod 3.
\\ (a) n <= 12: v_3 of the rational determinant det[binom(1/2, k - e)] (its reduction mod 3 is B_n).
\\ (b) n <= 60: B_n over F_3 directly from beta; reports the sizes with B_n != 0.
OUT = "research/results/bmd-20261009-z/ternary-induction-criterion.txt";
beta(m) = { if (m < 0, return(0)); my(d0 = m % 3, t = m \ 3); while(t, if(t % 3 == 2, return(0)); t \= 3); binomial(2, d0) };
En(n) = { my(L = List(), m = 0); while(#L < n, if(beta(m), listput(L, m)); m++); Vec(L) };
{
  for (n = 1, 12, my(e = En(n), t0 = n * (n - 1) / 2 + 2);
    my(B = matdet(matrix(n, n, i, j, binomial(1/2, t0 + i - 1 - e[j]))));
    write(OUT, "(a) n=", n, " E_n=", e, ": v_3 det[binom(1/2, k-e)] = ", valuation(B, 3)));
  my(good = List());
  for (n = 1, 60, my(e = En(n), t0 = n * (n - 1) / 2 + 2);
    my(B = matdet(matrix(n, n, i, j, Mod(beta(t0 + i - 1 - e[j]), 3))));
    if (B != 0, listput(good, n)));
  write(OUT, "(b) n = 1..60 with B_n != 0 mod 3: ", Vec(good));
}
