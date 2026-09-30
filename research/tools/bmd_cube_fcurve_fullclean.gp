\\ Fully symmetry-clean F-curve types (30 September 2026; route review bmd-20260930-zs).
\\ Caterpillar tails as in bmd_cube_fcurve_symclean.gp.  A type (a,b,c,d) is fully clean when no point of the curve,
\\ interior or special, carries an automorphism permuting the marks by an involution with at most f = N mod 2 fixed
\\ marks.  Types with two or more tails of size one have a chain special point (lem:cube-fcurve-symmetric-obstruction)
\\ and are excluded.  Interior: the rule mu of that lemma.  Special points (three pairings {X,Y}|{Z,W} of the tails):
\\  * no tail of size one: the tree has exactly two branch vertices H1 (tails X,Y) and H2 (tails Z,W); automorphisms
\\    permute the tails by a permutation preserving the pairing and sizes; fixed marks >= sum of phi over fixed tails;
\\  * exactly one tail of size one, A, paired with X: H1 has degree two and joins A to X, so the tree is a star with
\\    one branch vertex H2 and three caterpillar branches of sizes 1+|X|, |Z|, |W|; automorphisms permute equal-size
\\    branches; fixed marks >= sum of phi over fixed branches.
\\ In both cases the identity permutation counts only with a swap in some branch of size >= 2.  phi(1) = 1,
\\ phi(k) = k-2.  Question: do fully clean types span N_1(M_(0,N)-bar)^(S_N) for 8 <= N <= 60?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
fb(P, k, N) = my(c = 0); foreach ([[1, 2], [1, 3], [1, 4]], ij, my(t = P[ij[1]] + P[ij[2]]); if (t == k || t == N - k, c++)); for (i = 1, 4, if (P[i] == k || P[i] == N - k, c--)); c;
phi(k) = if (k == 1, 1, k - 2);
\\ minimal fixed marks over nontrivial size-preserving involutions of a list of branches, restricted by 'allowed'
minfixperm(S, perms) = {
  my(best = oo);
  foreach (perms, t,
    my(ok = 1); for (i = 1, #S, if (S[t[i]] != S[i] || t[t[i]] != i, ok = 0));
    if (ok, my(isid = (t == vector(#S, i, i)));
      if (!isid || vecmax(S) >= 2, best = min(best, sum(i = 1, #S, if (t[i] == i, phi(S[i]), 0))))));
  best;
}
allperms(n) = my(L = List()); forperm(n, p, listput(L, Vec(p))); Vec(L);
P4 = allperms(4); P3 = allperms(3);
interior(P) = minfixperm(P, P4);
special(P) = {
  my(best = oo, ones = select(x -> x == 1, P));
  foreach ([[1, 2, 3, 4], [1, 3, 2, 4], [1, 4, 2, 3]], pr,
    my(X = P[pr[1]], Y = P[pr[2]], Z = P[pr[3]], W = P[pr[4]]);
    if (#ones == 0,
      \\ permutations of (X,Y,Z,W) preserving the pairing {1,2}|{3,4}
      my(perms = [[1,2,3,4],[2,1,3,4],[1,2,4,3],[2,1,4,3],[3,4,1,2],[4,3,1,2],[3,4,2,1],[4,3,2,1]]);
      best = min(best, minfixperm([X, Y, Z, W], perms)),
      \\ exactly one single: it lies in one pair; merge it with its partner
      my(S = if (X == 1, [1 + Y, Z, W], if (Y == 1, [1 + X, Z, W], if (Z == 1, [1 + W, X, Y], [1 + Z, X, Y]))));
      best = min(best, minfixperm(S, P3))));
  best;
}
main() = {
  my(bad = List());
  for (N = 8, 60, my(K = N \ 2, f = N % 2, parts = List(), clean = List());
    forpart(p = N, listput(parts, Vec(p)), [1, N], [4, 4]);
    foreach (parts, P, if (#select(x -> x == 1, P) <= 1 && interior(P) > f && special(P) > f, listput(clean, P)));
    my(r = if (#clean, matrank(matrix(#clean, K - 1, i, j, fb(clean[i], j + 1, N))), 0));
    if (N <= 14, emit(Str("N=", N, ": fully clean types ", #clean, " of ", #parts, " (", Vec(clean), "), rank ", r, " of ", K - 1)));
    if (r < K - 1, listput(bad, N)));
  emit(Str("fully clean types fail to span for 8 <= N <= 60 at: ", Vec(bad)));
}
default(parisizemax, 2000000000);
main();
quit
