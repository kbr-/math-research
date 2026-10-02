\\ Tests of the route review of 8 October 2026 (cycle bmd-20261008-z) on gap (1) of the cone route.
\\ (a) Limit linear series: along one single-cherry arc (M = 2: roots 1, 1+3e, e, -2e^2), the leading coefficients of all
\\     6-minors of the pair matrix on columns 0..11 at the least valuation form the Plücker vector of the limit row space
\\     L0.  Reconstruct L0 from one nonzero coordinate (reduced row echelon form) and check that every leading coordinate
\\     equals the corresponding minor of L0 up to one common scalar; print the vanishing orders of L0 at T = 0 (the
\\     pivot columns of its echelon form from the left).
\\ (b) The initial minor p_{0..5} of the pair matrix of four generic roots a1..a4: its factorization over Q.
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
H(r, s, K) = { my(f = ((1 + r * 'x) * (1 + s * 'x))^(-3/2) + O('x^(K + 1))); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
pairmat(rts, K) = { my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k]))); P; }
{
\\ (a)
my(rts = [1, 1 + 3 * 'e, 'e, -2 * 'e^2], K = 11, P = pairmat(rts, K), R = 6, best = 1e9, lead = Map(), S0 = 0);
forsubset([K + 1, R], S, my(dt = matdet(vecextract(P, "..", Vec(S)))); if (dt != 0, my(vv = valuation(dt, 'e));
  if (vv < best, best = vv; lead = Map());
  if (vv == best, mapput(lead, Vec(S), polcoef(dt, vv, 'e)))));
my(keys = Vec(lead), L0 = 0, ok = 1, sc = 0);
\\ L0: the limit of the row space; build it as the leading part of the row space via a basis change: take the rows of
\\ P, and compute the limit of the row space as the span of the leading terms of an echelon basis over Q((e)).
my(E = matrix(R, K + 1, i, j, P[i, j]));
\\ Gaussian elimination over Q(e) with valuation pivoting, then leading terms
my(rowsL = List(), M2 = E);
for (step = 1, R,
  my(bi = 0, bj = 0, bv = 1e9);
  for (i = step, R, for (j = 1, K + 1, if (M2[i, j] != 0, my(vv = valuation(M2[i, j], 'e)); if (vv < bv || (vv == bv && j < bj), bv = vv; bi = i; bj = j))));
  my(tmp = M2[step, ]); M2[step, ] = M2[bi, ]; M2[bi, ] = tmp;
  M2[step, ] = M2[step, ] / M2[step, bj];
  for (i = 1, R, if (i != step && M2[i, bj] != 0, M2[i, ] = M2[i, ] - M2[i, bj] * M2[step, ])));
my(negv = 0);
L0 = matrix(R, K + 1, i, j, my(z = M2[i, j]); if (z == 0, 0, my(vv = valuation(z, 'e)); if (vv < 0, negv++; 0, if (vv > 0, 0, subst(numerator(z), 'e, 0) / subst(denominator(z), 'e, 0)))));
if (negv, emit(Str("(a) warning: ", negv, " entries of negative valuation after pivoting")));
for (t = 1, #keys, my(S = keys[t], mn = matdet(vecextract(L0, "..", S)), lc = mapget(lead, S));
  if (mn == 0, ok = 0, if (sc == 0, sc = lc / mn, if (lc / mn != sc, ok = 0))));
my(nz = 0); forsubset([K + 1, R], S, if (matdet(vecextract(L0, "..", Vec(S))) != 0, nz++));
my(ech = matimage(L0~)~, piv = List()); my(Ech = matrix(R, K + 1, i, j, L0[i, j]));
\\ vanishing orders at T = 0: pivots of the column echelon form from the left
my(rk = 0, pv = List()); for (j = 1, K + 1, if (matrank(vecextract(L0, "..", [1 .. j])) > rk, rk++; listput(pv, j - 1)));
emit(Str("(a) least valuation ", best, ", ", #keys, " leading coordinates; L0 reproduces them up to one scalar: ", ok,
  "; L0 has ", nz, " nonzero 6-minors; vanishing orders of L0 at T = 0: ", Vec(pv)));
\\ (b)
my(Pb = pairmat(['a1, 'a2, 'a3, 'a4], 5), Db = matdet(vecextract(Pb, "..", [1 .. 6])), F = factor(Db));
emit(Str("(b) initial minor of four roots: total degree ", poldegree(subst(subst(subst(subst(Db, 'a1, 't * 'a1), 'a2, 't * 'a2), 'a3, 't * 'a3), 'a4, 't * 'a4), 't),
  "; factors [total degree, multiplicity]: ", vector(#F[, 1], i, [poldegree(subst(subst(subst(subst(F[i, 1], 'a1, 't * 'a1), 'a2, 't * 'a2), 'a3, 't * 'a3), 'a4, 't * 'a4), 't), F[i, 2]]), "; differences dividing: ",
  sum(i = 1, #F[, 1], if (poldegree(subst(subst(subst(subst(F[i, 1], 'a1, 't * 'a1), 'a2, 't * 'a2), 'a3, 't * 'a3), 'a4, 't * 'a4), 't) == 1, F[i, 2], 0))));
}
quit
