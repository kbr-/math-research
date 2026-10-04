\\ Jacobi-Trudi lead entry three (cycle keu, 9 October 2026): when does the single-shift hierarchy decide?
\\ H_b = sum_(|S|=k+1) Vand(y_S)^2 h_b(y_S); claim: sum_b H_b z^b = A(z)/prod_i (1 - y_i z) with
\\ A(z) = sum_S Vand(y_S)^2 prod_(i not in S) (1 - y_i z), deg A <= M-k-1.
\\ (a) the identity, to order z^12, at two random rational clusters for M = 3..6 and every 1 <= k <= M-1 (exact);
\\ (b) at the M-th roots of unity (M = 3..9, k = 1..M-1, exact in Q(zeta_M)): whether A == 0, against the rotation
\\     criterion "the least residue b0 of -k(k+1) mod M exceeds M-k-1" (which implies A == 0).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
Aof(Y, k) = { my(s = 0); forsubset([#Y, k + 1], S, my(Z = vector(k + 1, i, Y[S[i]]), inS = vector(#Y)); for(i = 1, k + 1, inS[S[i]] = 1);
  s += vand(Z)^2 * prod(i = 1, #Y, if(inS[i], 1, 1 - Y[i] * 'z))); s; }
Gser(Y, k, n) = { my(s = 0); forsubset([#Y, k + 1], S, s += vand(vector(k + 1, i, Y[S[i]]))^2 * prod(i = 1, k + 1, 1 / (1 - Y[S[i]] * 'z + O('z^n)))); s; }
{
  setrand(20261009); my(bad = 0, tot = 0);
  for(M = 3, 6, for(rep = 1, 2, my(Y = vector(M, i, (random(41) - 20) / (random(5) + 1)));
    for(k = 1, M - 1, tot++; my(n = 13, lhs = Gser(Y, k, n), rhs = Aof(Y, k) * prod(i = 1, M, 1 / (1 - Y[i] * 'z + O('z^n))));
      if(lhs != rhs || poldegree(Aof(Y, k), 'z) > M - k - 1, bad++))));
  emit(Str("(a) identity and degree bound: ", tot - bad, " of ", tot, " cases hold (M = 3..6, every k, two clusters)"));
  for(M = 3, 9, my(Y = vector(M, j, Mod('w, polcyclo(M, 'w))^(j - 1)), silent = List(), pred = List());
    for(k = 1, M - 1, my(A = Aof(Y, k)); if(A == 0, listput(silent, k)); my(b0 = (-k * (k + 1)) % M); if(b0 > M - k - 1, listput(pred, k)));
    emit(Str("(b) M = ", M, " roots of unity: k with A == 0: ", Vec(silent), "; k predicted silent by rotation: ", Vec(pred))));
}
quit;
