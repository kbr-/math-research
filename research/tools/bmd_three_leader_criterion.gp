\\ Three-leader cherry step (cycle bmd-20261009-aj, 9 October 2026); uses the q-adic limit-space elimination of
\\ bmd_triple_tie_contact.gp (with another prime q, below).
\\ Tested statement (lem:cube-three-leader-criterion): at a rate where three leading cross coordinates tie, sharing
\\ 2M - 1 columns, the limit pair space is L0 = W + <v>, with W spanned by powers w^a (a in a set A0 of R - 1
\\ exponents) and v supported on the three remaining cross exponents b_1, b_2, b_3; L0 has a section vanishing to
\\ order R + 1 at T = 0 exactly when v is proportional to the Lagrange weights gamma_b = 1/prod_{a in A, a != b}(b - a),
\\ A = A0 + {b_1, b_2, b_3}.
\\ Arc: cherry {1, 1 + s q} above t q^2 (c0, 1, r q^2, r q^2 + m q^4), c0 = (1 + 2 sqrt(-2))/3 (excluded tie modulus,
\\ M = 4, R = 15), leading data (s, t, r, m) q-adic units; (1, 1, 1, 1) is the arc of check:cube-triple-tie-avoidance.
\\ Since L0 lies in the span of R + 2 powers (orders 0..R + 1), no section reaches order R + 2, so the arc avoids K for
\\ every v; the criterion decides only whether the slack is 1 or 0.
\\ Steps: (1) at (1,1,1,1), write L0 in the basis w^a (a in 0..8, -3, -3/2 + t for t in -6..7), find A0 and v,
\\ compare with gamma; (2) read off the monomial exponents of the ratios v_1/v_3, v_2/v_3 in each leading parameter;
\\ (3) v2/v3 is a Moebius function of t for fixed r (6 samples); solve for leading data with v proportional to gamma
\\ and recompute the vanishing orders of L0 there (prediction: maximal order exactly R + 1 = 16, never R + 2);
\\ control: the same data with s changed. A first run with 34 samples per r (stopped) gave degree 1 for r = 1, 2.
OUT = "research/results/bmd-20261009-aj/three-leader-criterion.txt";
\\ q = 1000121 = 2 mod 3 (every residue a cube, so s^6 needs only a square) with -2 a square; a first run with
\\ q = 1000003 found, for r = 1..30, a non-cube constant in s^6 and no solution (timed out).
q = 1000121; PREC = 120; K = 28;
H(r, s) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
vq(z) = valuation(z, q);
\\ Limit row space mod q (reduced rows) of the pair matrix of the roots rts.
limitspace(rts) = {
  my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j])); for (k = 1, K + 1, P[r, k] = h[k])));
  for (step = 1, R,
    my(bi = 0, bj = 0, bv = 10^9);
    for (i = step, R, for (j = 1, K + 1, if (P[i, j] != 0, my(vv = vq(P[i, j])); if (vv < bv || (vv == bv && j < bj), bv = vv; bi = i; bj = j))));
    my(tmp = P[step, ]); P[step, ] = P[bi, ]; P[bi, ] = tmp;
    P[step, ] = P[step, ] / P[step, bj];
    for (i = 1, R, if (i != step && P[i, bj] != 0, P[i, ] = P[i, ] - P[i, bj] * P[step, ])));
  matrix(R, K + 1, i, j, my(z = P[i, j]); if (z == 0, Mod(0, q), my(vv = vq(z)); if (vv > 0, Mod(0, q), if (vv < 0, error("negative valuation"), Mod(z, q)))));
}
orders(L) = { my(E = matimage(L~)~, B = matrix(#E[, 1], #E, i, j, E[i, j]));
  \\ vanishing orders = pivot columns of the row echelon form
  my(piv = List(), row = 1, nr = #B[, 1]);
  for (j = 1, #B, if (row > nr, break); my(p = 0); for (i = row, nr, if (B[i, j] != 0, p = i; break));
    if (p, my(t = B[row, ]); B[row, ] = B[p, ]; B[p, ] = t; B[row, ] = B[row, ] / B[row, j];
      for (i = 1, nr, if (i != row && B[i, j] != 0, B[i, ] = B[i, ] - B[i, j] * B[row, ])); listput(piv, j - 1); row++));
  Vec(piv); }
EXPS = concat(concat(vector(9, i, i - 1), [-3]), vector(14, i, -3/2 + i - 7));
bin(a, k) = prod(i = 0, k - 1, a - i) / k!;
BAS = matrix(#EXPS, K + 1, i, k, Mod(bin(EXPS[i], k - 1), q));
\\ Coordinates X with L = X * BAS, the exponents A0 with e_a in the row space, the support and vector v.
analyse(L) = {
  my(X = matinverseimage(BAS~, L~));
  if (#X == 0 || #X[1, ] != #L[, 1], return(0));
  X = X~;
  my(rk = matrank(X), A0 = List());
  for (a = 1, #EXPS, my(e = vector(#EXPS, i, Mod(i == a, q))); if (matrank(matconcat([X; e])) == rk, listput(A0, a)));
  my(rest = setminus([1 .. #EXPS], Set(Vec(A0))));
  my(Y = matrix(#X[, 1], #rest, i, j, X[i, rest[j]]), Ys = matimage(Y~)~);
  if (#Ys[, 1] != 1, return([Vec(A0), rest, #Ys[, 1]]));
  my(supp = select(j -> Ys[1, j] != 0, [1 .. #rest]));
  my(b = apply(j -> rest[j], supp), v = apply(j -> Ys[1, j], supp));
  my(A = concat(Vec(A0), b), g = apply(bi -> Mod(1 / prod(i = 1, #A, if (A[i] == bi, 1, EXPS[bi] - EXPS[A[i]])), q), b));
  [Vec(A0), b, v, g];
}
rootsfor(P) = { my([s, t, r, m] = P); concat([1, 1 + s * q], t * q^2 * [C0, 1, r * q^2, r * q^2 + m * q^4]); }
ratios(an) = [an[3][1] / an[3][3], an[3][2] / an[3][3]];
main() = {
  my(rr = sqrt(-2 + O(q^PREC))); C0 = truncate((1 + 2 * rr) / 3);
  my(base = [1, 1, 1, 1], L = limitspace(rootsfor(base)), an = analyse(L));
  write(OUT, "(1) base arc (1,1,1,1): vanishing orders ", orders(L));
  if (type(an) != "t_VEC" || #an < 4, write(OUT, "    L0 not of the form W + <v>: ", an); return);
  write(OUT, "    A0 = ", apply(i -> EXPS[i], an[1]), " (", #an[1], " exponents)");
  write(OUT, "    three exponents b = ", apply(i -> EXPS[i], an[2]), "; v = ", lift(an[3]), "; gamma = ", lift(an[4]));
  my(r0 = ratios(an), gr = [an[4][1] / an[4][3], an[4][2] / an[4][3]]);
  write(OUT, "    v proportional to gamma: ", r0 == gr);
  \\ (2) exponents of the ratios in each leading parameter
  my(EX = matrix(2, 4));
  for (p = 1, 4, my(P = base); P[p] = 2; my(a2 = analyse(limitspace(rootsfor(P))), r2 = ratios(a2));
    if (a2[2] != an[2], error("support moved"));
    for (k = 1, 2, my(f = r2[k] / r0[k], e = oo); for (x = -40, 40, if (Mod(2, q)^x == f, e = x; break)); EX[k, p] = e));
  write(OUT, "(2) exponents of (v1/v3, v2/v3) in (s, t, r, m) (oo: not a power of 2, so not a monomial): ", EX);
  \\ (3) v1/v3 = c1 s^6 t^-3 and v2/v3 = f(t, r), rational in t: reconstruct f from samples, solve f(t) = gamma2/gamma3,
  \\ then s^6 = (gamma1/gamma3) t^3 / c1.
  if (EX[1, 1] != 6 || EX[1, 2] != -3 || EX[1, 3] != 0 || EX[1, 4] != 0 || EX[2, 1] != 0 || EX[2, 4] != 0, error("unexpected exponents"));
  my(found = 0, NS = 6);
  for (r = 1, 40, if (found, break);
    my(T = vector(NS, i, i), F = vector(NS), c1 = 0, rec = 0);
    for (i = 1, NS, my(ai = analyse(limitspace(rootsfor([1, T[i], r, 1]))));
      if (type(ai) != "t_VEC" || #ai < 4 || ai[2] != an[2], write(OUT, "    sample t = ", T[i], ", r = ", r, ": structure changed: ", ai); return); my(ri = ratios(ai)); F[i] = ri[2]; if (i == 1, c1 = ri[1]));
    for (d = 1, (NS - 4) \ 2, if (rec, break);
      my(A = matrix(NS, 2 * d + 2, i, j, if (j <= d + 1, Mod(T[i], q)^(j - 1), -F[i] * Mod(T[i], q)^(j - d - 2))), k = matker(A));
      if (#k, my(c = k[, 1]); rec = [Pol(Vecrev(c[1 .. d + 1]), 'y), Pol(Vecrev(c[d + 2 .. 2 * d + 2]), 'y), d]));
    if (!rec, write(OUT, "(3) r = ", r, ": no rational reconstruction of degree <= ", (NS - 4) \ 2); next);
    my(rts = polrootsmod(rec[1] - gr[2] * rec[2], q));
    write(OUT, "(3) r = ", r, ": v2/v3 = P/Q in t of degree ", rec[3], " (fits ", NS, " samples); roots of P - (gamma2/gamma3) Q: ", lift(rts));
    foreach(rts, tt, if (!found && tt != 0 && subst(rec[2], 'y, tt) != 0,
      my(s6 = gr[1] * tt^3 / c1, ss = polrootsmod('z^6 - lift(s6), q));
      write(OUT, "    t = ", lift(tt), ": ", #ss, " sixth roots of s^6");
      if (#ss, found = [lift(ss[1]), lift(tt), r, 1]))));
  if (!found, write(OUT, "    no degenerate leading data found"); return);
  my(Lb = limitspace(rootsfor(found)), ab = analyse(Lb), ob = orders(Lb));
  write(OUT, "    degenerate arc data ", found, ": vanishing orders ", ob, "; max = R + 1 = 16: ", vecmax(ob) == 16, "; max >= R + 2 (K): ", vecmax(ob) >= 17);
  if (#ab >= 4, write(OUT, "    v proportional to gamma there: ", ratios(ab) == [ab[4][1] / ab[4][3], ab[4][2] / ab[4][3]]));
  my(Pc = found); Pc[1] = Pc[1] + 1;
  my(oc = orders(limitspace(rootsfor(Pc))));
  write(OUT, "    control ", Pc, ": vanishing orders ", oc, "; max >= 16: ", vecmax(oc) >= 16);
}
main();
