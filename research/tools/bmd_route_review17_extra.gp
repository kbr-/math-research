\\ Route review cheap tests (9 October 2026; cycle bmd-20261009-j), M = 4, nested cherries (1, 1+eta, 1+eta+eta^3, 3).
\\ (a) Total-positivity lead: at a real point (eta = 1/100, u = 1/1000), are the signs of all cross coordinates P_Lambda
\\     (columns [-4, 7], series to u^20) given by a product rule sign = s(p) * (-1)^(sum Lambda)? Reports the sign
\\     counts per p and parity class; a single sign per (p, parity) class is necessary for a total-positivity reading.
\\ (b) Orbital-energy (Aufbau) bridge: along arcs, with omega = arc value (q-adic, q = 1000003 = eta), is the exchange
\\     cost Delta(a, b) = omega(W - a + b) - omega(W) at the best window W additive, Delta(a,b) = e(b) - e(a)?
\\     Tests the 2x2 relation Delta(a,b) + Delta(a',b') = Delta(a,b') + Delta(a',b) over all pairs.
OUT = "research/results/bmd-20261009-j/review-extra.txt";
c(n) = if(n < 0, 0, binomial(-3/2, n));
NU = 20;
coordpoly(Y, L) = { my(M = #Y);
  matdet(matrix(2 * M, 2 * M, r, i, my(t = L[i]);
    if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
      my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m)))) };
{
  my(M = 4, cols = [-M .. 2 * M - 1], e = 1/100, Y = [1, 1 + e, 1 + e + e^3, 3], cnt = Map());
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]), p = #select(t -> t < 0, L));
    if(p <= M, my(val = subst(coordpoly(Y, L), 'u, 1/1000));
      if(val != 0, my(key = [p, vecsum(L) % 2, sign(val)]); mapput(cnt, key, if(mapisdefined(cnt, key), mapget(cnt, key), 0) + 1))));
  write(OUT, "(a) signs at eta = 1/100, u = 1/1000: [p, parity of sum Lambda, sign] -> count");
  foreach(Vec(cnt), k, write(OUT, "   ", k, " -> ", mapget(cnt, k)));
}
{
  my(M = 4, q = 1000003, cols = [-M .. 2 * M - 1], Y = [1, 1 + q, 1 + q + q^3, 3], H = Map());
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]));
    if(#select(t -> t < 0, L) <= M, my(D = coordpoly(Y, L)); mapput(H, L, vector(NU + 1, n, my(x = polcoef(D, n - 1, 'u)); if(x == 0, oo, valuation(x, q))))));
  my(om(L, wx, we) = my(v, val = oo, LL = vecsort(L)); if(!mapisdefined(H, LL, &v), return(oo));
    for (n = 0, NU, if(v[n + 1] < oo, val = min(val, (vecsum(LL) + n) * wx + n * we + v[n + 1]))); val);
  write(OUT, "(b) additivity of exchange costs at the best window, nested cherries M = 4:");
  foreach([[1, 1], [1, 3], [3, 1], [1, 9], [9, 1]], ar, my(wx = ar[1], we = ar[2], bw = oo, W);
    for (p = 0, M, my(Wp = [-p .. 2 * M - 1 - p], w = om(Wp, wx, we)); if(w < bw, bw = w; W = Wp));
    my(out = setminus(Set(cols), Set(W)), ins = Set(W), Dl = matrix(#ins, #out), tot = 0, bad = 0);
    for (i = 1, #ins, for (j = 1, #out, Dl[i, j] = om(concat(setminus(ins, [ins[i]]), [out[j]]), wx, we) - bw));
    for (i = 1, #ins, for (i2 = i + 1, #ins, for (j = 1, #out, for (j2 = j + 1, #out,
      my(a = Dl[i, j] + Dl[i2, j2], b = Dl[i, j2] + Dl[i2, j]); if(a < oo && b < oo, tot++; if(a != b, bad++))))));
    write(OUT, "   arc (", wx, ",", we, "): best window ", W, ", finite 2x2 relations ", tot, ", non-additive ", bad));
}
