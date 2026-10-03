\\ Goal-level review tests (cycle bmd-20261009-as, 9 October 2026).
\\ (1) Falsification attempt for thm:cube-hankel-valuation-wide-support on the q-adic trees of
\\     check:cube-cancellation-wide-support (q = 1000081, fixed reparametrized roots Y, so h_p = q-valuation of
\\     Hank_(M-p)(Y) with weight 1). At the 900 rates (a/10, b/10): the number of rates where (H1) fails, and, at every
\\     rate where the recorded leaders' union exceeds 2M+1 (from wide-support.txt), whether (H1) holds and the union lies
\\     in [-p*-1, 2M-p*] for the least minimizer p* of b.
\\ (2) Double cancellation: distinct points (0, 1, a, b) with Hank_1 = Hank_2 = 0 (M = 4), by resultants over Q.
OUT = "research/results/bmd-20261009-as/review-tests.txt";
q = 1000081;
hank(Y, k) = { my(M = #Y, s = 0); forsubset([M, k + 1], S, my(v = prod(i = 1, k + 1, prod(j = i + 1, k + 1, Y[S[j]] - Y[S[i]]))); s += v^2); s; }
bw(M, p, wx, we) = wx * (2*M^2 - 2*M*p + p^2 - p) + we * (p^2 - p + M);
test(name, Y, recorded) = {
  my(M = #Y, h = vector(M, p, my(z = hank(Y, M - p)); if (z == 0, oo, valuation(z, q))), fails = 0, okrec = 0);
  foreach(concat(vector(30, a, vector(30, c, [a / 10, c / 10]))), w,
    my(bs = vector(M, p, bw(M, p, w[1], w[2])), bstar = vecmin(bs));
    my(h1 = #select(p -> bs[p] + h[p] <= bstar + w[1], [1 .. M]) > 0);
    if (!h1, fails++));
  foreach(recorded, r, my([w, U] = r, bs = vector(M, p, bw(M, p, w[1], w[2])), bstar = vecmin(bs));
    my(ps = select(p -> bs[p] == bstar, [1 .. M])[1], h1 = #select(p -> bs[p] + h[p] <= bstar + w[1], [1 .. M]) > 0);
    my(inside = vecmin(U) >= -ps - 1 && vecmax(U) <= 2*M - ps);
    if (h1 && inside, okrec++);
    write(OUT, "     ", name, " at ", w, ": p* = ", ps, ", (H1) ", h1, ", leaders' union ", [vecmin(U), vecmax(U)], " inside [", -ps - 1, ", ", 2*M - ps, "]: ", inside));
  write(OUT, "(1) ", name, ": h_p = ", h, "; (H1) fails at ", fails, " of 900 rates; recorded large unions consistent: ", okrec, " of ", #recorded);
}
{
  my(w = truncate((-1 + sqrt(-3 + O(q^30))) / 2), r2 = sqrt(-2 + O(q^30)));
  my(trip = [-4, -3, -2, -1, 0, 1, 2, 3, 4, 5]);
  test("equilateral (1,w,w^2)", [1, w, w^2], []);
  test("tie modulus (1+2sqrt(-2))/3", [truncate((1 + 2 * r2) / 3), 1, q, q + q^2], [[[1, 1/2], trip]]);
  test("tie modulus (1-2sqrt(-2))/3", [truncate((1 - 2 * r2) / 3), 1, q, q + q^2], [[[1, 1/2], trip]]);
  test("three-root level (1,w,w^2) over q", [1, w, w^2, q], [[[2, 1], trip]]);
  my(H1 = hank([0, 1, 'a, 'b], 1), H2 = hank([0, 1, 'a, 'b], 2), R = polresultant(H1, H2, 'b), sols = List());
  foreach(factor(R)[, 1], f, if (poldegree(f, 'a) > 0,
    foreach(polroots(f), a0, my(bs = polroots(subst(H1, 'a, a0)));
      foreach(bs, b0, if (abs(subst(subst(H2, 'a, a0), 'b, b0)) < 1e-20 * (1 + abs(b0))^8,
        my(pts = [0, 1, a0, b0], d = vecmin(concat(vector(4, i, vector(4 - i, j, abs(pts[i] - pts[i + j]))))));
        listput(sols, [a0, b0, d]))))));
  my(dist = select(s -> s[3] > 1e-8, Vec(sols)));
  write(OUT, "(2) M = 4, (0,1,a,b): resultant factors ", apply(f -> poldegree(f, 'a), factor(R)[, 1]~), "; common zeros found ", #sols, ", with distinct points ", #dist);
  for (i = 1, min(#dist, 3), write(OUT, "     a = ", dist[i][1], ", b = ", dist[i][2]));
}
