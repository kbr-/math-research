\\ Exact iterated coface limit for statement 2's slice d=2 (cycle kbm, 9 October 2026).
\\ Lemma (merge order limit): the saturated eps-limit of span{T^a : a in S} + x span{T^b : b in S'},
\\ x = sqrt(1+eps T), is span{T^e : e in Ord(S,S')}, Ord = orders at t=0 of
\\ span{t^a} + sqrt(1+t) span{t^b} over F_p.
\\ Degree two: the trivial character T_s and the single characters S_s evolve as
\\ T_{s+1} = Ord(T_s, S_s), S_{s+1} = Ord(S_s, {0}), from T_0 = {0,1}, S_0 = {0}; pairs stay {0}.
\\ After n steps only T_n remains; T_n = {0..N-1}, N = 2+n+n(n-1)/2, implies Delta_{n,2} != 0 mod p.
\\ Reported per p: the steps s whose T_s, S_s are not consecutive, and the first such n.

ordset(S, S1, p) = {
  my(r = #S1, prec = 2 * (vecmax(concat(S, S1)) + #S + r) + 40, sq, M, ords = List(), used, piv);
  sq = Vecrev(truncate(sqrt(Mod(1, p) + t + O(t^prec))));
  if(#sq < prec, sq = concat(sq, vector(prec - #sq, i, Mod(0, p))));
  \\ rows sqrt(1+t) t^b with the monomials t^a (a in S) removed: the S-rows already have orders S
  M = matrix(r, prec, i, j, if(j - 1 >= S1[i], sq[j - S1[i]], Mod(0, p)));
  for(i = 1, r, for(k = 1, #S, M[i, S[k] + 1] = 0));
  \\ lowest-order echelon of the remaining rows
  used = vector(r);
  for(j = 1, prec,
    piv = 0;
    for(i = 1, r, if(!used[i] && M[i, j] != 0, piv = i; break));
    if(piv,
      used[piv] = 1; listput(ords, j - 1);
      for(i = 1, r, if(!used[i] && M[i, j] != 0, M[i, ] = M[i, ] - M[i, j] / M[piv, j] * M[piv, ]))));
  if(#ords < r, error("precision too small"));
  vecsort(concat(S, Vec(ords)));
}

consec(S) = S == vector(#S, i, i - 1);

{
foreach([3, 5, 7, 1000003], p,
  my(T = [0, 1], S = [0], badT = List(), badS = List());
  for(s = 1, 30,
    my(T2 = ordset(T, S, p), S2 = ordset(S, [0], p));
    T = T2; S = S2;
    if(#T != 2 + s + s * (s - 1) / 2, error("dimension"));
    if(!consec(T), listput(badT, s));
    if(!consec(S), listput(badS, s));
    if(s <= 8 && p == 3, print("p=3 s=", s, " T_s=", T, " S_s=", S)));
  print("p=", p, " non-consecutive T_n for n<=30: ", Vec(badT), "; non-consecutive S_s: ", Vec(badS)));
}
quit;
