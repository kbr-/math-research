\\ Taylor cofactor zeros at distinct roots, and the forced C-block tie (cycle bmd-20261009-bn, 9 October 2026).
\\ Claim tested (prop:cube-cblock-spread-bound): along an arc of the normalized cluster y(s), the leading C-block
\\ coordinate (least w_x * sum(S) + val p_S) is unique at every rate w_x > 0 iff the flat limit of the pair span has the
\\ same pivot set as the generic member; in particular, an arc that ends at a distinct-root point y* with F(y*) = 0 but
\\ has F(y(s)) != 0 forces a tie at some rate.
\\ (1) F(0, 1, a, b) = p_T0 / Vand^2 at M = 4 as a polynomial in a, b; its factorization; one distinct-root zero.
\\ (2) At that zero y*, the arc y* + s*v (v generic), exact s-adic valuations of all 13C6 = 1716 coordinates p_S,
\\     S subset [0, 12]; the lower envelope of v_S + w * sum(S) over w > 0 and its breakpoints (ties).
OUT = "research/results/bmd-20261009-bn/taylor-cofactor-zeros.txt";
default(parisizemax, 4 * 10^9);
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
pairmat(Y, K) = {
  my(M = #Y, R = M * (M - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, M, for (j = i + 1, M, r++; my(h = H(Y[i], Y[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  P;
}
{
  my(M = 4, R = 6, Y = [0, 1, 'a, 'b], P = pairmat(Y, R - 1), T = matdet(P), V = prod(i = 1, M, prod(j = i + 1, M, Y[i] - Y[j]))^(M - 2));
  my(F = T / V);
  \\ full symmetric cofactor at M = 4 in all four variables, compared with the pairing product
  my(Y4 = ['y1, 'y2, 'y3, 'y4], T4 = matdet(pairmat(Y4, R - 1)), V4 = prod(i = 1, 4, prod(j = i + 1, 4, Y4[i] - Y4[j]))^2, F4 = T4 / V4);
  my(Pp = ('y1 + 'y2 - 'y3 - 'y4) * ('y1 + 'y3 - 'y2 - 'y4) * ('y1 + 'y4 - 'y2 - 'y3));
  write(OUT, "(0) M = 4: F(y1..y4) / prod over pairings (y_i + y_j - y_k - y_l) = ", F4 / Pp);
  write(OUT, "(1) M = 4: F(0, 1, a, b) has total degree ", poldegree(subst(subst(F, 'a, 't * 'a), 'b, 't * 'b), 't), "; factorization:");
  my(fa = factor(F));
  for (i = 1, #fa~, write(OUT, "    ", fa[i, 1], "  ^", fa[i, 2]));
  \\ a distinct-root zero: fix a = 3, solve F(0,1,3,b) = 0 over Q-bar; take a real root
  my(Fb = subst(F, 'a, 3), rts = polrootsreal(Fb));
  write(OUT, "    F(0, 1, 3, b) = ", factor(Fb), "; real roots b = ", rts);
  \\ pick an irreducible factor of F(0,1,3,b) of degree >= 1 not giving a coincidence, work in its number field
  my(fb = factor(Fb)[, 1], g = 0);
  for (i = 1, #fb, my(q = fb[i]); if (poldegree(q, 'b) >= 1 && subst(q, 'b, 0) != 0 && subst(q, 'b, 1) != 0 && subst(q, 'b, 3) != 0, g = q; break));
  write(OUT, "    chosen factor g(b) = ", g, " (b0 a root; y* = (0, 1, 3, b0) has distinct coordinates)");
  \\ (2) arc y* + s*v, v = (1, 2, -1, 5), in the number field Q[b]/g, s-adic valuations
  \\ (a first run used b0 = Mod(b, g) and 25 columns; Mod-wrapped constants break s-adic valuations, so the rational
  \\ root is used, and 13 columns suffice for the sets that can lead)
  my(K = R + 6, NS = 12, b0 = -polcoef(g, 0, 'b) / polcoef(g, 1, 'b), vv = [1, 2, -1, 5]);
  my(Ys = vector(4, i, [0, 1, 3, b0][i] + vv[i] * 's + O('s^NS)));
  my(PP = matrix(R, K + 1), r = 0);
  for (i = 1, M, for (j = i + 1, M, r++;
    my(f = ((1 + Ys[i] * 'x + O('x^(K + 1))) * (1 + Ys[j] * 'x))^(-3/2));
    for (k = 1, K + 1, PP[r, k] = polcoef(f, k - 1, 'x))));
  my(vals = List(), cnt = 0);
  forsubset([K + 1, R], S, my(Sv = Vec(S), m = matdet(matrix(R, R, i, j, PP[i, Sv[j]])), v = if (m == 0, oo, valuation(m, 's)));
    if (v < oo, listput(vals, [v, vecsum(Vec(S)) - R, Vec(S)])); cnt++);  \\ column indices 1-based: sum(S) - R = sum of 0-based columns
  my(vl = Vec(vals), vmin = vecmin(apply(z -> z[1], vl)));
  write(OUT, "(2) arc y* + s v at M = 4, columns [0, ", K, "]: ", cnt, " coordinates, ", #vl, " with finite valuation (< ", NS, "); least valuation ", vmin);
  my(S0 = 0, s0sum = oo); foreach(vl, z, if (z[1] == vmin && z[2] < s0sum, s0sum = z[2]; S0 = z));
  my(Sinf = 0, sinfsum = oo); foreach(vl, z, if (z[2] < sinfsum, sinfsum = z[2]; Sinf = z));
  write(OUT, "    flat-limit pivot (least column sum at least valuation): S0 = ", apply(t -> t - 1, S0[3]), ", val ", S0[1], ", column sum ", S0[2]);
  write(OUT, "    generic pivot (least column sum overall): ", apply(t -> t - 1, Sinf[3]), ", val ", Sinf[1], ", column sum ", Sinf[2]);
  \\ lower envelope breakpoints over w in (0, 20]
  my(env = List(), prevS = -1);
  forstep (w = 1/50, 20, 1/50, my(best = oo, arg = List());
    foreach(vl, z, my(f = z[1] + w * z[2]); if (f < best, best = f; arg = List([z[3]]), if (f == best, listput(arg, z[3]))));
    if (#arg > 1, listput(env, [w, apply(S -> apply(t -> t - 1, S), Vec(arg))])));
  write(OUT, "    rates w in {1/50, ..., 20} with a tie (more than one leader): ", if (#env, Vec(env), "none"));
}
