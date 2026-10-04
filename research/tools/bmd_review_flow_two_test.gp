\\ Route review (cycle kfd, 9 October 2026): flow order two at the non-polygon cluster z^5 + z + 1.
\\ (a) Exact, from power sums p_n of the roots (polsym): H_mu = +- det[p_(a+b)]_(a <= k, b in mu + delta) for k = 1, 2,
\\     mu in {(), (1), (2), (1,1)}. Prediction: Hank_k = H_() = 0 and H_(1) = D Hank_k/(2k) = 0 (flow order 2 at p = 4, 3),
\\     H_(2) = 0 (the single raise by two is silent) and H_(1,1) != 0 (the two-column raise carries the order).
\\ (b) Numerical, 120 digits: the window's next coefficient [eps^(B_p+1)] P_(Lambda_p) / Vand^2 at x = 1 (every term at
\\     eps^(B_p+1) has x-degree A_p + 1), for p = 3, 4; (F) at rate (3,2) needs it to vanish. Control: the same at p = 2,
\\     where the flow order is 0.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 120);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
f = 'z^5 + 'z + 1; M = 5;
ps = polsym(f, 30);  \\ ps[n+1] = p_n
pw(n) = ps[n + 1];
Hmu(k, mu) = { my(m = concat(mu, vector(k + 1 - #mu)), B = vector(k + 1, c, m[c] + k + 1 - c)); matdet(matrix(k + 1, k + 1, a, j, pw(a - 1 + B[j]))); }
coefeps(ys, L, B) = {
  my(M = #ys, K = 2 * M * (B + 1) + 1, s0 = 0);
  for (j = 0, K - 1, my(e = exp(2 * Pi * I * j / K), G = matrix(2*M, 2*M));
    for (s = 1, M, for (u = 1, 2*M, my(t = L[u]);
      G[s, u] = if (t >= 0, cc(t) * ys[s]^t, 0);
      G[M + s, u] = sum(r = max(1, -t), B + 1, cc(r) * cc(t + r) * e^r * ys[s]^(t + r))));
    s0 += matdet(G) * e^(-B));
  s0 / K;
}
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
{
  foreach([1, 2], k, emit(Str("(a) k=", k, " (p=", M - k, "): H_() = ", Hmu(k, []), ", H_(1) = ", Hmu(k, [1]), ", H_(2) = ", Hmu(k, [2]), ", H_(1,1) = ", Hmu(k, [1, 1]))));
  my(Y = polroots(f), V = vand(Y)^2);
  foreach([2, 3, 4], p, my(B = p^2 - p + M, L = vector(2 * M, i, -p - 1 + i), c0 = coefeps(Y, L, B) / V);
    my(c1 = coefeps(Y, L, B + 1) / V);
    emit(Str("(b) p=", p, ": |least coefficient| ", Strprintf("%.6g", abs(c0)), "; |next coefficient [eps^(B+1)]| ", Strprintf("%.6g", abs(c1)))));
}
quit;
