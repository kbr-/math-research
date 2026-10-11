\\ Tested statement (preprint of 5 October 2026, outline, Step 3): for squarefree primary n in Z[w],
\\ w = exp(2 pi i/3), prime to 6,
\\   mu(n) gamma_{-1}(n) = chi_n(-1) G(n)^{-1} conj(alpha(n)) gamma_2(n),
\\ with gamma_j(n) = N(n)^{-1/2} sum_{x mod n} chi_n(x)^j e(x/n), e(z) = exp(4 pi i Im(z)/sqrt 3),
\\ chi_n the sextic residue symbol, alpha(n) = n/|n|, G(n) = conj(chi_n(4)) gamma_3(n).
\\ Everything is computed from these definitions; the control replaces conj(alpha) by alpha.
\\ Output: one line per n: norm, number of prime factors, |lhs - rhs|, |lhs - control|.
default(realprecision, 30);
rhK = nfinit(rhy^2 + rhy + 1);
rhw = exp(2*Pi*I/3);
rhemb(v) = my(c = lift(Mod(v, rhy^2 + rhy + 1))); polcoeff(c, 0) + polcoeff(c, 1)*rhw;
\\ primary generator (congruent to 1 mod 3) of a prime ideal prime to 3
rhprimary(pr) =
{
  my(g = nfbasistoalg(rhK, bnfisprincipal(bnfinit(rhK.pol), pr)[2]), u);
  for(k = 0, 5, u = lift(g * Mod(-rhy, rhy^2 + rhy + 1)^k);
    if((polcoeff(u, 0) - 1) % 3 == 0 && polcoeff(u, 1) % 3 == 0, return(u)));
  error("no primary generator");
}
\\ sextic symbol (x/pr)_6 as a complex number, 0 if pr divides x
rhsym(x, pr, mp, q) =
{
  my(r = nfmodpr(rhK, x, mp), t);
  if(r == 0, return(0));
  t = r^((q - 1)/6);
  for(k = 0, 5, if(nfmodpr(rhK, Mod(-rhy, rhy^2 + rhy + 1)^k, mp) == t, return((-rhw)^k)));
  error("no sixth root");
}
rhtest(prs) =
{
  my(m = #prs, gens, n, nc, N, mps, qs, g, chim1, chi4, lhs, rhs, ctl, al, c, x, xe, ex);
  gens = vector(m, i, rhprimary(prs[i]));
  n = lift(Mod(prod(i = 1, m, gens[i]), rhy^2 + rhy + 1)); nc = rhemb(n); N = round(norm(nc));
  mps = vector(m, i, nfmodprinit(rhK, prs[i])); qs = vector(m, i, idealnorm(rhK, prs[i]));
  g = vector(4);  \\ sums for j = -1, 2, 3
  my(sm1 = 0, s2 = 0, s3 = 0);
  for(a = 0, N - 1, for(b = 0, N - 1,
    x = a + b*rhy; c = prod(i = 1, m, rhsym(x, prs[i], mps[i], qs[i]));
    if(c != 0, xe = (a + b*rhw)/nc; ex = exp(4*Pi*I*imag(xe)/sqrt(3));
      sm1 += conj(c)*ex; s2 += c^2*ex; s3 += c^3*ex)));
  \\ each residue class mod n is counted N times
  sm1 /= N*sqrt(N); s2 /= N*sqrt(N); s3 /= N*sqrt(N);
  chim1 = prod(i = 1, m, rhsym(-1, prs[i], mps[i], qs[i]));
  chi4 = prod(i = 1, m, rhsym(4, prs[i], mps[i], qs[i]));
  al = nc/abs(nc);
  lhs = (-1)^m * sm1;
  rhs = chim1 * chi4 / s3 * conj(al) * s2;
  ctl = chim1 * chi4 / s3 * al * s2;
  print(N, " ", m, " ", abs(lhs - rhs), " ", abs(lhs - ctl), " |g2|=", abs(s2), " |g3|=", abs(s3));
}
{
  my(P7 = idealprimedec(rhK, 7), P13 = idealprimedec(rhK, 13), P19 = idealprimedec(rhK, 19),
     P31 = idealprimedec(rhK, 31), P5 = idealprimedec(rhK, 5), P11 = idealprimedec(rhK, 11));
  rhtest([P7[1]]); rhtest([P7[2]]); rhtest([P13[1]]); rhtest([P19[1]]); rhtest([P31[2]]);
  rhtest([P5[1]]); rhtest([P11[1]]);
  rhtest([P7[1], P7[2]]); rhtest([P7[1], P13[1]]); rhtest([P7[2], P19[1]]); rhtest([P13[1], P19[2]]);
  rhtest([P5[1], P7[1]]); rhtest([P13[2], P31[1]]);
  rhtest([P7[1], P7[2], P13[1]]);
  print("done 14");
}
