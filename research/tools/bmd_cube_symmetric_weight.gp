\\ Symmetric mark weight (30 September 2026; cycle bmd-20260930-r).
\\ Tested statement (theorem in the entry): let b_1..b_N be distinct and stable under b -> -b, N = 2m + f,
\\ f = 1 meaning b = 0 is one of them. The pair space V = <((1+b_iT)(1+b_jT))^(-3/2) : i<j> (dim R = C(N,2))
\\ splits into even and odd series, and its vanishing sequence at T = 0 (the mark) is bounded below by
\\   N = 2m:     {0, ..., 2m^2-2m-1} U {2m^2-2m, 2m^2-2m+2, ..., 2m^2-2},
\\   N = 2m+1:   {0, ..., 2m^2-1}    U {2m^2, 2m^2+2, ..., 2m^2+2m-2},
\\ so the mark has weight at least m(m-1)/2. Here we compute the actual sequence at random symmetric
\\ configurations over F_p (orders = the L with rank A_L > rank A_(L-1)) and compare it with the bound
\\ (equality means the bound is attained generically on the symmetric locus). Control: a random
\\ non-symmetric configuration must give 0..R-1.
\\ Part 2: the pencil cubic det[1, x1+x2, x1 x2; 1, x3+x4, x3 x4; 1, x5+x6, x5 x6] is irreducible over Q.
\\ Part 3: on the first line of DATA.gp, the boundary polynomial F(a(u)) is prime to J(u).
p = 2^61 - 1;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta32(m) = binomial(-3/2, m);
Hk(k, x, y) = sum(m = 0, k, beta32(m) * beta32(k - m) * x^m * y^(k - m));
prs(N) = my(v = List()); for (i = 1, N, for (j = i + 1, N, listput(v, [i, j]))); Vec(v);
Amat(b, L) = my(P = prs(#b)); matrix(#P, L + 1, r, k, Hk(k - 1, b[P[r][1]], b[P[r][2]]));
orders(b) = {
  my(R = #b * (#b - 1) / 2, res = List(), prev = 0, L = -1);
  while (#res < R, L++; my(r = matrank(Amat(b, L))); if (r > prev, listput(res, L)); prev = r;
    if (L > 3 * R, error("no full rank")));
  Vec(res);
}
bound(N) = {
  my(m = N \ 2);
  if (N % 2 == 0, concat(vector(2*m^2 - 2*m, i, i - 1), vector(m, t, 2*m^2 - 2*m + 2*(t - 1))),
    concat(vector(2*m^2, i, i - 1), vector(m, t, 2*m^2 + 2*(t - 1))));
}
weight(o) = sum(i = 1, #o, o[i] - (i - 1));
main() = {
  setrand(20260930);
  for (N = 4, 10,
    my(m = N \ 2, be = vector(m, k, Mod(random(p), p)), b = List());
    for (k = 1, m, listput(b, be[k]); listput(b, -be[k]));
    if (N % 2, listput(b, Mod(0, p)));
    b = Vec(b);
    my(o = orders(b), bd = bound(N), gen = orders(vector(N, i, Mod(random(p), p))));
    emit(Str("N=", N, " m=", m, ": symmetric sequence tail ", o[max(1, #o - m - 1)..#o], ", weight ", weight(o),
      "; bound weight ", weight(bd), ", sequence equals bound: ", o == bd,
      "; control (random configuration) weight ", weight(gen))));
  my(x = vector(6, i, eval(Str("x", i))));
  my(C = matdet([1, x[1] + x[2], x[1] * x[2]; 1, x[3] + x[4], x[3] * x[4]; 1, x[5] + x[6], x[5] * x[6]]));
  my(f = factor(C));
  emit(Str("pencil cubic: total degree 3, irreducible factors over Q: ", #f~, " (exponents ", f[, 2]~, ")"));
  read("research/results/bmd-20260930-r/lines/data.gp");
  my(P = prs(6), us = vector(50, t, Mod(t + 3, p)));
  my(Fv = vector(#us, t, my(a = vector(6, i, A[1, i] + B[1, i] * us[t]));
    matdet(Amat(a, 14)) / prod(r = 1, 15, (a[P[r][1]] - a[P[r][2]])^4)));
  my(Fu = polinterpolate(us, Fv, 'u));
  my(a = vector(6, i, Mod(A[1, i], p) + Mod(B[1, i], p) * 'u), J = 1);
  foreach ([[[1,2],[3,4],[5,6]],[[1,2],[3,5],[4,6]],[[1,2],[3,6],[4,5]],[[1,3],[2,4],[5,6]],[[1,3],[2,5],[4,6]],
            [[1,3],[2,6],[4,5]],[[1,4],[2,3],[5,6]],[[1,4],[2,5],[3,6]],[[1,4],[2,6],[3,5]],[[1,5],[2,3],[4,6]],
            [[1,5],[2,4],[3,6]],[[1,5],[2,6],[3,4]],[[1,6],[2,3],[4,5]],[[1,6],[2,4],[3,5]],[[1,6],[2,5],[3,4]]], mu,
    J *= matdet(matrix(3, 3, r, c, [1, a[mu[r][1]] + a[mu[r][2]], a[mu[r][1]] * a[mu[r][2]]][c])));
  emit(Str("line 1: deg F(a(u)) = ", poldegree(Fu), ", deg J = ", poldegree(J), ", deg gcd(F, J) = ", poldegree(gcd(Fu, J))));
}
main();
