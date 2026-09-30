\\ Far polynomials along the eleven-root merge chain (2 October 2026; review cycle bmd-20261002-b).
\\ Functions copied from bmd_cube_merge_far.gp (cycle bmd-20261001-t); only the case list differs: the far
\\ spaces F(n,k) of the chain merges at N = 11 not covered before, (n,k) = (2,9), (3,8), (4,7), (6,5), (7,4).
\\ Output per case: [dim, interpolation checks, Q square, deg R, deg gcd(R,R'), ord at 0, ord at 1 of Q].
\\ Far limit of a single merge (1 October 2026; cycle bmd-20261001-t).
\\ lem:cube-single-merge: V(n; p_0; p_1..p_k) with p_0 = 0, p_1 = eps, p_2..p_k fixed.  In the merge chart z = eps w the
\\ classes, by monodromy around w = 0 and w = 1, are (constants and fixed nonzero powers of eps removed):
\\   T  (trivial): 1, eps w, (eps w)^-i (i = 1..C, C = binom(n,2)), and for 2 <= j < l: ((1 - eps w/p_j)(1 - eps w/p_l))^(1/2)
\\   0  (sqrt w):  for j >= 2, i < n: (eps w)^-i (1 - eps w/p_j)^(1/2)
\\   1  (sqrt(w-1)): for j >= 2: (1 - eps w/p_j)^(1/2)
\\   01 (sqrt(w(w-1))): (eps w)^-i, i < n.
\\ Prediction (hierarchical attainment): the far limit F(n,k) is
\\   T: w^-C .. w^(1+P), P = binom(k-1,2);  0: sqrt(w) w^-(n-1) Pol_(<(k-1)n)(w);  1: sqrt(w-1) Pol_(<k-1)(w);
\\   01: sqrt(w(w-1)) w^-(n-1) Pol_(<n)(w),
\\ free of moduli.  Part A computes the exact flat limits over Q for small (n,k) at generic p_j and compares.
\\ Part B: for the predicted F(n,k), modulo p = 2^61 - 1: det^2 w^d0 (w-1)^d1 = W^2 (det the Wronskian with the square-root
\\ factors divided out; d0, d1 the numbers of functions with a sqrt(w), resp. sqrt(w-1) factor) is rational;
\\ clearing w and w-1 gives R^2 with R the polynomial of non-branch Weierstrass points (w != 0, 1).  Reports deg R (their
\\ number with multiplicity), deg gcd(R, R') (0 iff all are simple) and the orders of the cleared quotient at w = 0, 1.
default(parisizemax, 2000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
PR = 2^61 - 1;
default(threadsizemax, 400000000);
TE = 40;
\\ flat limit of rows given as series in 'e with Laurent-polynomial coefficients in 'w
flatlim(rows) = {
  my(k = #rows, D = 60, R = rows, iter = 0);
  R = vector(k, i, my(v = valuation(R[i], 'e)); R[i] * 'e^(-v));
  my(vz(f) = Vecrev(f * 'w^D, 2 * D + 1));
  while (1, iter++; if (iter > 2000, error("no convergence"));
    my(M = matrix(k, 2 * D + 1, i, j, vz(polcoef(R[i], 0, 'e))[j]), K = matker(M~));
    if (#K == 0, return(vector(k, i, polcoef(R[i], 0, 'e))));
    my(c = K[, 1], piv = 0); for (i = 1, k, if (c[i] != 0, piv = i));
    my(nr = sum(i = 1, k, c[i] * R[i]));
    if (polcoef(nr, 0, 'e) != 0, error("relation"));
    R[piv] = nr / 'e);
}
sq(x) = (1 + x + O('e^TE))^(1/2);
farclasses(n, k, P) = {
  my(C = n * (n - 1) / 2, T = List(), Z = List(), Ol = List(), ZO = List());
  listput(T, 1 + O('e^TE)); listput(T, 'e * 'w + O('e^TE));
  for (i = 1, C, listput(T, ('e * 'w)^(-i) + O('e^TE)));
  for (j = 2, k, for (l = j + 1, k, listput(T, sq(-'e * 'w / P[j]) * sq(-'e * 'w / P[l]))));
  for (j = 2, k, for (i = 0, n - 1, listput(Z, ('e * 'w)^(-i) * sq(-'e * 'w / P[j]))));
  for (j = 2, k, listput(Ol, sq(-'e * 'w / P[j])));
  for (i = 0, n - 1, listput(ZO, ('e * 'w)^(-i) + O('e^TE)));
  [Vec(T), Vec(Z), Vec(Ol), Vec(ZO)];
}
predicted(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  [vector(C + 2 + P, t, 'w^(t - 1 - C)), vector((k - 1) * n, t, 'w^(t - n)), vector(k - 1, t, 'w^(t - 1)), vector(n, t, 'w^(t - n))];
}
samespan(A, B) = {
  my(D = 80, vz(f) = Vecrev(f * 'w^D, 2 * D + 1), MA = Mat(apply(vz, A)~), MB = Mat(apply(vz, B)~));
  matrank(MA) == #A && matrank(concat(MA, MB)) == #A && #A == #B;
}
\\ Part B: Weierstrass polynomial of the predicted far space
wronsq(F, w0, d) = {
  my(fac = [0, 1/2, 0, 1/2; 0, 0, 1/2, 1/2], M = matrix(d, d), row = 0, x0 = Mod(w0, PR));
  for (c = 1, 4, my(g = 1 + O('T^(d + 2)));
    if (fac[1, c], g *= (1 + 'T / x0 + O('T^(d + 2)))^(1/2));
    if (fac[2, c], g *= (1 + 'T / (x0 - 1) + O('T^(d + 2)))^(1/2));
    foreach (F[c], f, row++; my(s = subst(f, 'w, x0 + 'T) * g); for (m = 1, d, M[row, m] = polcoef(s, m - 1, 'T))));
  my(d0 = #F[2] + #F[4], d1 = #F[3] + #F[4]);
  matdet(M)^2 * x0^d0 * (x0 - 1)^d1;
}
\\ all functions are multiplied by w^s (s = max(C, n-1)), which multiplies W by w^(s d) and makes them polynomials
farpoly(nk) = {
  my(n = nk[1], k = nk[2], C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, s = max(C, n - 1), pos = max(max(1 + P, (k - 2) * n), k - 2));
  my(F = apply(v -> apply(f -> f * 'w^s, v), predicted(n, k)), d = sum(c = 1, 4, #F[c]), A = d * (d - 1), DB = 2 * d * (s + pos) + d + 20 + 2 * A, pts = vector(DB + 4, i, 3 + 5 * i));
  \\ W^2 has poles of order at most d(d-1) at w = 0 and w = 1 (derivatives of the square-root factors): clear them
  my(vals = vector(#pts, i, wronsq(F, pts[i], d) * Mod(pts[i], PR)^A * Mod(pts[i] - 1, PR)^A));
  my(Q = polinterpolate(pts[1..DB + 1], vals[1..DB + 1], 'x), ok = prod(i = DB + 2, #pts, subst(Q, 'x, pts[i]) == vals[i]));
  my(a = 0, b = 0);
  while (poldegree(Q) > 0 && subst(Q, 'x, 0) == 0, Q = Q / 'x; a++);
  while (poldegree(Q) > 0 && subst(Q, 'x, 1) == 0, Q = Q / ('x - 1); b++);
  my(S = 0, isq = issquare(Q, &S));
  [d, ok, isq, if (isq, poldegree(S), -1), if (isq, poldegree(gcd(S, deriv(S, 'x))), -1), a, b];
}
export(PR, wronsq, predicted, farpoly);
{
  my(cases = [[2, 9], [3, 8], [4, 7], [6, 5], [7, 4]]);
  my(res = parapply(farpoly, cases));
  for (i = 1, #cases, emit(Str("  (n,k)=", cases[i], ": ", res[i])));
}
quit
