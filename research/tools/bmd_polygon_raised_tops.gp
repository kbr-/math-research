\\ Newton/roots-of-unity lead entry two (cycle key, 9 October 2026): which raises of the top k columns lead at a polygon.
\\ For the regular M-gon (centred at 0) and 2 <= k <= M-2 (p = M-k, N = 2M-p), raise the top k columns N-k..N-1 by a
\\ partition lambda (at most k parts, lambda_1 on the top column) and compute tau = [eps^(B_p)] P_L / Vand^2 at x = 1
\\ (every term at eps^(B_p) has x-degree A_p + |lambda|, lem:cube-polygon-raise-selection, so x = 1 loses nothing).
\\ Numerical, 120 digits, complex; |tau| < 1e-60 is reported as zero. Cases: M = 5 (k = 2, 3) and M = 7 (k = 2) at every
\\ weight w <= k(M-k-1) allowed by the lemma (M | k(k+1) + w), plus a control cluster where nothing should vanish.
\\ Prediction (thm:cube-polygon-schur-hankel-residue with the multi-column expansion): every weight below k(M-k-1)
\\ vanishes; at weight k(M-k-1) the rectangle lambda = ((M-k-1)^k) is nonzero.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 120);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
\\ [eps^B] det G(eps): G is polynomial in eps of degree <= B per entry, so det has degree <= 2MB; evaluate at the
\\ K = 2MB+1 roots of unity in eps and take the discrete Fourier coefficient (numeric determinants only).
coefeps(ys, L, B) = {
  my(M = #ys, K = 2 * M * B + 1, s0 = 0);
  for (j = 0, K - 1, my(e = exp(2 * Pi * I * j / K), G = matrix(2*M, 2*M));
    for (s = 1, M, for (u = 1, 2*M, my(t = L[u]);
      G[s, u] = if (t >= 0, cc(t) * ys[s]^t, 0);
      G[M + s, u] = sum(r = max(1, -t), B, cc(r) * cc(t + r) * e^r * ys[s]^(t + r))));
    s0 += matdet(G) * e^(-B));
  s0 / K;
}
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
setL(M, p, k, la) = { my(N = 2 * M - p, J = vector(N, i, i - 1));
  for (c = 1, #la, J[N - c + 1] += la[c]); concat(vector(p, i, -p - 1 + i), J); }
{
  setrand(20261009);
  foreach([[5, 2], [5, 3], [7, 2]], mk, my(M = mk[1], k = mk[2], p = M - k, B = p^2 - p + M, R = k * (M - k - 1));
    my(Y = vector(M, j, exp(2 * Pi * I * (j - 1) / M)), Yc = vector(M, j, (random(200) - 100) / 37.), V = vand(Y)^2, Vc = vand(Yc)^2);
    for (w = 0, R, if ((k * (k + 1) + w) % M, next);
      forpart(q = w, my(la = Vecrev(q), t = coefeps(Y, setL(M, p, k, la), B) / V, tc = coefeps(Yc, setL(M, p, k, la), B) / Vc);
        emit(Str("M=", M, " k=", k, " w=", w, " lambda=", la, ": |tau| at polygon ", if (abs(t) < 1e-60, "0", Strprintf("%.6g", abs(t))),
          "; at control ", Strprintf("%.6g", abs(tc)))), , [1, k])));
}
quit;
