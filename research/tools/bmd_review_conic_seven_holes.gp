\\ Falsification test of the goal-level route review of cycle kea (9 October 2026): the seven-hole criterion for the
\\ n = 5 conic space Z_d (lem:cube-two-pair-confluence; apolarity lead of the conic holes review).
\\ Statement tested.  For d >= 3, on the conic w1^2 = l1 = 1+a1 T, w3^2 = l3 = 1+a3 T, the complete series
\\   H = Pol_{<=4d-3} + (w1/l1) Pol_{<=4d-3} + w3 Pol_{<=4d-4} + (w1 w3/l1) Pol_{<=4d-3}      (dimension 16d-9)
\\ contains Z_d = F<l3^2, w3 l1, w1 l3^2/l1, w1 w3>, F = Pol_{<=4d-5} (dimension N = 16d-16), as the common kernel of the
\\ seven functionals A(-1/a3), A'(-1/a3), B(-1/a3), B'(-1/a3), C(-1/a1), D(-1/a1), [T^(4d-3)] D on f = A + (w1/l1) B
\\ + w3 C + (w1 w3/l1) D.  Hence Z_d is normal at T = 0 (on the branch w1 = w3 = 1) iff the 7 x 7 matrix of these
\\ functionals on a basis of the 7-dimensional space K = {f in H : ord_{T=0} f >= N} is nonsingular.
\\ Test: for d = 3..8, every odd p <= 16d and three random (a1,a3) in GF(p^e), p^e > 10^5 (seed as in cycle kbt), assert
\\ dim K = 7, compute the 7 x 7 determinant and the direct N x N Hasse determinant of Z_d, and report any disagreement
\\ of their vanishing.  Prediction: no disagreement, and both vanish at every sample only at (d,p) = (6,3).
default(parisizemax, 2000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
pick(g) = { my(a1, a3); until(a1 != 0 && a3 != 0 && a1 != a3, a1 = random(g); a3 = random(g)); [a1, a3]; }
coeffs(s, N) = vector(N, c, polcoeff(s, c - 1, T));
test(a1, a3, d, o) = {
  my(N = 16 * d - 16, l1 = o + a1 * T + O(T^N), l3 = o + a3 * T + O(T^N), w1 = sqrt(l1), w3 = sqrt(l3));
  my(nA = 4 * d - 2, nB = 4 * d - 2, nC = 4 * d - 3, nD = 4 * d - 2, R = List());
  for(i = 0, nA - 1, listput(R, coeffs(o * T^i + O(T^N), N)));
  for(i = 0, nB - 1, listput(R, coeffs(w1 / l1 * T^i, N)));
  for(i = 0, nC - 1, listput(R, coeffs(w3 * T^i, N)));
  for(i = 0, nD - 1, listput(R, coeffs(w1 * w3 / l1 * T^i, N)));
  my(M = matrix(#R, N, i, j, R[i][j]), K = matker(M~));   \\ M: (16d-9) x N; K: coefficient vectors x with x M = 0
  if(#K != 7, error(Str("dim K = ", #K)));
  my(x3 = -1 / a3, x1 = -1 / a1, ev(v, x) = sum(i = 1, #v, v[i] * x^(i - 1)), dv(v, x) = sum(i = 2, #v, (i - 1) * v[i] * x^(i - 2)));
  my(F = matrix(7, 7, r, j, my(k = K[, j], A = k[1..nA], B = k[nA + 1..nA + nB], C = k[nA + nB + 1..nA + nB + nC], D = k[nA + nB + nC + 1..#k]);
    [ev(A, x3), dv(A, x3), ev(B, x3), dv(B, x3), ev(C, x1), ev(D, x1), D[nD]][r]));
  my(gens = [l3^2, w3 * l1, w1 * l3^2 / l1, w1 * w3], Z = List());
  for(g = 1, 4, for(i = 0, 4 * d - 5, listput(Z, coeffs(gens[g] * T^i, N))));
  [matdet(F) != 0, matdet(matrix(#Z, N, i, j, Z[i][j])) != 0];
}
SAMPLES = 3;
setrand(20261009);
{
for(d = 3, 8,
  my(bad = List(), dis = 0, tot = 0);
  forprime(p = 3, 16 * d,
    my(e = ceil(log(1e5) / log(p)), g = ffgen(p^e, 'y), o = g^0, z = 0);
    for(k = 1, SAMPLES,
      my(a = pick(g), r = test(a[1], a[2], d, o));
      tot++; if(r[1] != r[2], dis++); if(!r[2], z++));
    if(z == SAMPLES, listput(bad, p)));
  emit(Str("d=", d, " samples=", tot, " disagreements=", dis, " primes with zero determinant at all samples: ", Vec(bad))));
}
quit;
