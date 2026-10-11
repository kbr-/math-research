\\ Tested statement (preprint of 5 October 2026, its equation labelled crt-a, in the form used in its
\\ reduction): for coprime squarefree primary v, m in Z[w] prime to 6,
\\   gamma_2(v m) = gamma_2(v) gamma_2(m) chi_m(v)^4 ,
\\ with gamma_2(n) = N(n)^{-1/2} sum_{x mod n} chi_n(x)^2 e(x/n), e(z) = exp(4 pi i Im(z)/sqrt 3), chi_n the
\\ sextic residue symbol (so chi^2 is the cubic one and chi_m(v)^4 = conj of the cubic symbol (v/m)_3).
\\ alpha(n) = n/|n| is multiplicative on primary elements, so the same relation holds for
\\ conj(alpha) gamma_2.  The control replaces chi_m(v)^4 by chi_m(v)^2.
\\ Output: one line per pair: N(v), N(m), |lhs - rhs|, |lhs - control|.
default(realprecision, 30);
rhK = nfinit(rhy^2 + rhy + 1);
rhB = bnfinit(rhy^2 + rhy + 1);
rhw = exp(2*Pi*I/3);
rhsym(x, mp, q) =
{
  my(r = nfmodpr(rhK, x, mp), t);
  if(r == 0, return(0));
  t = r^((q - 1)/6);
  for(k = 0, 5, if(nfmodpr(rhK, Mod(-rhy, rhy^2 + rhy + 1)^k, mp) == t, return((-rhw)^k)));
  error("no sixth root");
}
rhprimary(pr) =
{
  my(g = nfbasistoalg(rhK, bnfisprincipal(rhB, pr)[2]), u);
  for(k = 0, 5, u = lift(g * Mod(-rhy, rhy^2 + rhy + 1)^k);
    if((polcoeff(u, 0) - 1) % 3 == 0 && polcoeff(u, 1) % 3 == 0, return(u)));
  error("no primary generator");
}
rhemb(v) = polcoeff(v, 0) + polcoeff(v, 1)*rhw;
\\ gamma_2 of the product of the primary generators of the prime ideals prs
rhgamma2(prs) =
{
  my(m = #prs, n, nc, N, mps, qs, s = 0, c);
  n = lift(Mod(prod(i = 1, m, rhprimary(prs[i])), rhy^2 + rhy + 1)); nc = rhemb(n); N = round(norm(nc));
  mps = vector(m, i, nfmodprinit(rhK, prs[i])); qs = vector(m, i, idealnorm(rhK, prs[i]));
  for(a = 0, N - 1, for(b = 0, N - 1,
    c = prod(i = 1, m, rhsym(a + b*rhy, mps[i], qs[i]));
    if(c != 0, s += c^2*exp(4*Pi*I*imag((a + b*rhw)/nc)/sqrt(3)))));
  s/(N*sqrt(N));
}
rhpair(pv, pm) =
{
  my(v = rhprimary(pv), mp = nfmodprinit(rhK, pm), q = idealnorm(rhK, pm), c = rhsym(v, mp, q), lhs, base);
  lhs = rhgamma2([pv, pm]); base = rhgamma2([pv]) * rhgamma2([pm]);
  print(idealnorm(rhK, pv), " ", q, " ", abs(lhs - base*c^4), " ", abs(lhs - base*c^2));
}
{
  my(P7 = idealprimedec(rhK, 7), P13 = idealprimedec(rhK, 13), P19 = idealprimedec(rhK, 19),
     P31 = idealprimedec(rhK, 31), P5 = idealprimedec(rhK, 5));
  rhpair(P7[1], P13[1]); rhpair(P13[1], P7[1]); rhpair(P7[2], P19[1]); rhpair(P13[2], P19[2]);
  rhpair(P7[1], P7[2]); rhpair(P5[1], P7[1]); rhpair(P7[1], P31[1]); rhpair(P13[1], P31[2]);
  print("done 8");
}
