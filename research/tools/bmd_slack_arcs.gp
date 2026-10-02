\\ Slack along explicit arcs (8 October 2026; cycle bmd-20261008-za).
\\ For each arc (a vector of roots, polynomials in eps), the pair matrix rows H_k(r, s) = [T^k]((1+rT)(1+sT))^(-3/2) on
\\ the columns 0..R+1+EXT; prints the least minor valuation, whether the initial minor attains it, and the best slack
\\ R + 1 - max L over least sets L.  Arcs: single-cherry arcs (M = 2) generic and inside the hyperplane
\\ a1 + a3 = a2 + a4 of the initial minor, where the slack-2 property must fail.
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
H(r, s, K) = { my(f = ((1 + r * 'x) * (1 + s * 'x))^(-3/2) + O('x^(K + 1))); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
{
my(EXT = 3, arcs = [["generic cherry", [1, 1 + 3 * 'e, 'e, -2 * 'e^2]],
                     ["cherry on a1+a3=a2+a4", [1, 1 + 'e + 2 * 'e^2, 'e, -2 * 'e^2]],
                     ["cherry on a1+a3=a2+a4, other rates", [1, 1 + 2 * 'e^2 + 3 * 'e^5, 2 * 'e^2, -3 * 'e^5]]]);
foreach(arcs, A, my(rts = A[2], n = #rts, R = n * (n - 1) / 2, K = R + 1 + EXT, P = matrix(R, K + 1), r = 0, best = 1e9, init = -1, sl = -99);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  forsubset([K + 1, R], S, my(dt = matdet(vecextract(P, "..", Vec(S)))); if (dt != 0, my(vv = valuation(dt, 'e));
    if (vv < best, best = vv; sl = -99);
    if (vv == best, sl = max(sl, R + 1 - (vecmax(Vec(S)) - 1)))));
  my(d0 = matdet(vecextract(P, "..", [1 .. R])));
  emit(Str(A[1], ": least valuation ", best, ", initial minor ", if (d0 == 0, "identically zero", Str("valuation ", valuation(d0, 'e))), ", best slack ", sl)));
}
quit
