\\ Cheap test of the Stohr-Voloch lead in the goal-level route review of cycle kbw (9 October 2026).
\\ Prediction: Z_6 (the n=5 two-pair conic space, N=80) mod 3 has generic corank one, so its order sequence at a
\\ general point is {0..78} plus one order e >= 80.  By the p-adic criterion (every mu digitwise below an order
\\ in base p is an order), e must be a power of 3, the least being 81.  Computed: the orders of Z_6 at T=0 at a
\\ random point of GF(3^11), jets up to 120; control p=5 (orders 0..79).

rows(a1, a3, d, P, o) = {
  my(l1 = o + a1 * T + O(T^P), l3 = o + a3 * T + O(T^P), w1 = sqrt(l1), w3 = sqrt(l3), gens, R = List());
  gens = [l3^2, w3 * l1, w1 * l3^2 / l1, w1 * w3];
  for(g = 1, 4, for(i = 0, 4 * d - 5, listput(R, gens[g] * T^i)));
  Vec(R);
}

orders(p, e, d, P) = {
  my(g = ffgen(p^e, 'y), o = g^0, a1, a3, Rw, M, ords = List(), rk = 0);
  until(a1 != 0 && a3 != 0 && a1 != a3, a1 = random(g); a3 = random(g));
  Rw = rows(a1, a3, d, P, o);
  M = matrix(#Rw, P, i, c, polcoeff(Rw[i], c - 1, T));
  for(c = 1, P, my(k = matrank(M[, 1..c])); if(k > rk, listput(ords, c - 1); rk = k));
  Vec(ords);
}

default(parisizemax, 2^31);
setrand(20261009);
{
foreach([[3, 11], [5, 8]], pe,
  my(o = orders(pe[1], pe[2], 6, 120), n = #o);
  print("p=", pe[1], ": ", n, " orders; first gap after ", o[n - 1], "; last orders ", o[max(1, n - 2)..n]));
}
quit;
