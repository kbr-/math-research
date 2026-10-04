\\ Route review (cycle kep, 9 October 2026): where the joint order of the triple window's pair sequences levels off.
\\ Continues bmd_review_triple_joint_profile.gp to degrees q = 11..24 (least order r, searched below the previous
\\ degree's order, since a recurrence of degree q is one of degree q+1), and gives each single g_ij's own least order
\\ at q = 24.  Modulo p = 1000003, as before: "none" is rigorous for the stated (r, q).  The window has five columns:
\\ a joint recurrence of order <= 5 is what the counting route needs; a floor above five rules it out at every degree
\\ up to the tested one.
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
  my(t = #X, nun = (r + 1) * (q + 1), per = nun \ t + 10);
  if(K0 + per + r > #X[1], return(-1));
  my(A = matrix(t * per, nun, i, j, my(w = (i - 1) \ per + 1, k = K0 + (i - 1) % per, s = (j - 1) \ (q + 1), e = (j - 1) % (q + 1)); Mod(k, p)^e * X[w][k + s + 1]));
  #matker(A) > 0;
}
least(X, K0, q, rmax) = { for(r = 1, rmax, my(h = has(X, K0, r, q)); if(h == -1, return(-1)); if(h, return(r))); 0; }
{
  foreach([[2, 5, -3], [1/3, -4, 7/2]], av, for(m = 2, 3,
    my(X = seqs(av, m, 700), K0 = 3 * m + 5, prof = List(), r0 = 12);
    for(q = 11, 24, my(r = least(X, K0, q, r0)); listput(prof, [q, r]); if(r > 0, r0 = r));
    emit(Str("roots ", av, " m=", m, ": joint [q, least r]: ", Vec(prof)));
    emit(Str("   single g_12, g_13, g_23: least order at q = 24: ", vector(3, w, least([X[w]], K0, 24, 12))))));
}
quit;
