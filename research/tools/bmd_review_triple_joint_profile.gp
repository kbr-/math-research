\\ Route review (cycle kep, 9 October 2026): the true minimal joint recurrences of the triple window's pair sequences.
\\ g_ij(M) = [T^M] P(T) Phi_ij(T) (lem:cube-level-window-reduction), three pairs of three roots.  A recurrence
\\ sum_{s<=r} P_s(M) x(M+s) = 0 with deg P_s <= q annihilating all three sequences.  For q = 0..10 report the least
\\ order r <= 30 for which one exists on M = K0.. (overdetermined, computed modulo the prime p; a full-rank system mod p
\\ is full rank over Q, so "none" is rigorous for the stated (r, q); a kernel mod p is evidence of one over Q).
\\ Tests the claim of entry-2026-10-09-cube-triple-joint-order that the joint order is six: differential order
\\ (= q) versus recurrence order (= r) are different quantities.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
p = 1000003;
lam = 3/2;
seqs(av, m, N) = {
  my(P = prod(l = 1, 3, (1 + av[l] * 'T)^m), pr = [[1, 2], [1, 3], [2, 3]]);
  vector(3, w, my(a = av[pr[w][1]], b = av[pr[w][2]], s = ((1 + a * 'T) * (1 + b * 'T) + O('T^N))^(-lam), rho = Mod(1, p), c = vector(N));
    for(k = 0, N - 1, if(k > 0, rho *= Mod(k, p) / Mod(k + lam - m, p)); c[k + 1] = rho * Mod(polcoef(s, k, 'T), p));
    my(S = Mod(1, p) * P * Ser(c, 'T)); vector(N, k, polcoef(S, k - 1, 'T)));
}
has(X, K0, r, q) = {
  my(nun = (r + 1) * (q + 1), per = nun \ 3 + 10);
  if(K0 + per + r > #X[1], return(-1));
  my(A = matrix(3 * per, nun, i, j, my(w = (i - 1) \ per + 1, k = K0 + (i - 1) % per, s = (j - 1) \ (q + 1), e = (j - 1) % (q + 1)); Mod(k, p)^e * X[w][k + s + 1]));
  #matker(A) > 0;
}
{
  foreach([[2, 5, -3], [1/3, -4, 7/2]], av, for(m = 2, 3,
    my(X = seqs(av, m, 420), K0 = 3 * m + 5, prof = List());
    for(q = 0, 10, my(found = 0); for(r = 1, 30, my(h = has(X, K0, r, q)); if(h == -1, break); if(h, found = r; break)); listput(prof, [q, found]));
    emit(Str("roots ", av, " m=", m, ": [degree q, least joint order r (0 = none up to 30)]: ", Vec(prof)))));
}
quit;
