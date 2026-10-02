\\ Hankel determinants of the binomial coefficients c_n = binomial(-lambda, n) (7 October 2026; cycle bmd-20261007-zf).
\\ The minimal terms of the confluent cherry's reduced expansion factor over blocks into 2x2 and 3x3 Hankel
\\ determinants det[c_(u+r+s)]_(r,s<h) (h = 2, 3).  Prints their factorization as functions of lambda (symbolic) for
\\ u = 0..6, normalized by c_u c_(u+1) ... (the product of the diagonal leading entries), to expose a product formula.
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
cn(n) = prod(z = 0, n - 1, -L - z) / n!;
{
foreach([2, 3], h,
  for (u = 0, 6,
    my(H = matdet(matrix(h, h, r, s, cn(u + r + s - 2))), nrm = prod(r = 0, h - 1, cn(u + r)));
    emit(Str("h = ", h, ", u = ", u, ": det / prod_(r<h) c_(u+r) = ", factor(H / nrm)))));
}
