\\ Appell lead entry two (cycle keo, 9 October 2026): minimal recurrence orders of the triple window's pair sequences.
\\ Phi(T) = sum_k rho_k e_k T^k (pair row ((1+aT)(1+bT))^(-3/2), rho_k = k!/Gamma(k+5/2-m)), Psi = (1+aT)^m (1+bT)^m Phi.
\\ For each, find the least order r and polynomial degree q such that a recurrence sum_{s<=r} P_s(k) x_(k+s) = 0 with
\\ deg P_s <= q holds for k = K0..K1 (overdetermined linear system, exact over Q).  Single rows: (1+aT)^m Phi_single is
\\ a polynomial plus a rational part (lem:cube-level-window-reduction), the model for what a pair might do.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
G(x) = if(x == 1/2, 1, if(x > 1/2, (x - 1) * G(x - 1), G(x + 1) / x));
seqs(a, b, m, N) = {
  my(s = ((1 + a * 'T) * (1 + b * 'T) + O('T^N))^(-3/2), c = vector(N, k, (k - 1)! / G(k - 1 + 5/2 - m) * polcoef(s, k - 1, 'T)));
  my(Phi = Ser(c, 'T), Psi = (1 + a * 'T)^m * (1 + b * 'T)^m * Phi);
  [c, vector(N, k, polcoef(Psi, k - 1, 'T))];
}
\\ least (r, q) with a recurrence on x[K0..] (unknowns: (r+1)(q+1) coefficients); returns [r, q] or [-1,-1]
order(x, K0) = {
  for(tot = 1, 8, for(r = 1, tot, my(q = tot - r, nun = (r + 1) * (q + 1), rows = nun + 12);
    if(K0 + rows + r > #x, next);
    my(A = matrix(rows, nun, i, j, my(k = K0 + i - 1, s = (j - 1) \ (q + 1), e = (j - 1) % (q + 1)); k^e * x[k + s + 1]));
    if(#matker(A) > 0, return([r, q]))));
  [-1, -1];
}
{
  foreach([[2, 5], [-3, 7/2]], ab, for(m = 2, 4,
    my(S = seqs(ab[1], ab[2], m, 140), K0 = 3 * m + 5);
    emit(Str("(a,b)=", ab, " m=", m, ": Phi order ", order(S[1], K0), "; Psi=(1+aT)^m(1+bT)^m Phi order ", order(S[2], K0)))));
}
quit;
