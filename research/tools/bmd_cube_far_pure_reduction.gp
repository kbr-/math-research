\\ Pure-class reduction of the merge far spaces (2 October 2026; cycle bmd-20261002-c).
\\ F(n,k) = A1 + A2 + B3 + B4 with A1 = <w^-C..w^(1+P)>, A2 = w^(1/2) w^-(n-1) Pol_(<(k-1)n), B3 = (w-1)^(1/2) Pol_(<k-1),
\\ B4 = (w(w-1))^(1/2) w^-(n-1) Pol_(<n).  A = A1 + A2 is spanned by monomials w^e, e in E (q = |E| distinct exponents),
\\ killed by L = prod_(e in E) (theta - e), theta = w d/dw.  Claim: W(F) = W(A) W(L B3 + L B4) up to powers of w, and
\\ L maps (1-w)^(1/2) w^s p to (1-w)^(1/2-q) times a polynomial; so the far points are the zeros off {0,1} of the
\\ Wronskian of P3 + w^(1/2) P4, where (1-w)^(1/2-q) P3 = L B3 and (1-w)^(1/2-q) w^(1/2) P4 = L B4.
\\ Test 1: W(A) has no zeros off {0,1} (computed in this cycle's scratch test; repeated here).
\\ Test 2: the reduced Wronskian's non-branch polynomial equals R_(n,k) (exact, over Q).
\\ Test 3: other unions of classes containing A1 have non-branch Wronskian zeros.
\\ Output also the dimensions and the degrees of the polynomials P3, P4.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
strip(N) = { while (subst(N, 'w, 0) == 0, N = N / 'w); while (subst(N, 'w, 1) == 0, N = N / ('w - 1)); N / pollead(N); }
wr(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  strip(numerator(matdet(M)));
}
\\ theta - e applied to (1-w)^alpha w^beta p(w), returned as the new polynomial with alpha - 1 (beta unchanged)
thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
reduce(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)), q = #E);
  my(P3 = vector(k - 1, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); p));
  my(P4 = vector(n, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 1/2 - (n - 1), E[i]); al--); p));
  \\ the reduced space: P3 (integral at 0) + w^(1/2 - (n-1)) P4; the common factor (1-w)^(1/2-q) is dropped
  my(Rred = wr([[0, 0, P3], [1/2, 0, apply(p -> p * 'w^(-(n - 1)), P4)]]));
  my(F = [[0, 0, vector(C + 2 + P, t, 'w^(t - 1 - C))], [1/2, 0, vector((k - 1) * n, t, 'w^(t - n))],
    [0, 1/2, vector(k - 1, t, 'w^(t - 1))], [1/2, 1/2, vector(n, t, 'w^(t - n))]]);
  my(RA = wr([F[1], F[2]]), R = wr(F));
  emit(Str("(n,k)=", [n, k], ": q=", q, " reduced dimension ", n + k - 1, " (full ", sum(c = 1, 4, #F[c][3]), "); non-branch zeros of W(A): ", poldegree(RA),
    "; reduced polynomial equals R_(n,k): ", Rred == R, " (deg ", poldegree(R), "); deg P3 ", apply(poldegree, P3), ", deg P4 ", apply(poldegree, P4)));
}
foreach([[1, 3], [1, 4], [2, 3], [3, 3], [2, 4], [4, 3]], v, reduce(v[1], v[2]));
\\ Test 3: non-branch zeros of the Wronskians of other unions of classes containing A1
unions(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  my(F = [[0, 0, vector(C + 2 + P, t, 'w^(t - 1 - C))], [1/2, 0, vector((k - 1) * n, t, 'w^(t - n))],
    [0, 1/2, vector(k - 1, t, 'w^(t - 1))], [1/2, 1/2, vector(n, t, 'w^(t - n))]]);
  emit(Str("(n,k)=", [n, k], ": non-branch zeros of W for classes {1,2}: ", poldegree(wr([F[1], F[2]])), ", {1,3}: ", poldegree(wr([F[1], F[3]])),
    ", {1,4}: ", poldegree(wr([F[1], F[4]])), ", {1,2,3}: ", poldegree(wr([F[1], F[2], F[3]])), ", {1,2,4}: ", poldegree(wr([F[1], F[2], F[4]]))));
}
foreach([[2, 3], [3, 3], [2, 4], [4, 3]], v, unions(v[1], v[2]));
