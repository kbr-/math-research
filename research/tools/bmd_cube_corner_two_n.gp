\\ Vertex minors of the (2,n) neck corners (2 October 2026; cycle bmd-20261002-j).
\\ Neck (2,n): x = (0, lambda), y_j = lambda' s'_j (s'_1 = 0, s'_2 = 1, others symbolic).  Rows: B_l = divided
\\ difference of B(y) = sum_b beta_b y^b (z-1)^-b over y_1..y_(l+1), and A_1 B_l with A_1 = sum_(a>=1) alpha_a lambda^(a-1) z^-a
\\ (alpha_a, beta_b the coefficients of (1-x)^(1/2)), l < n.  Columns: principal parts at 0 and 1 and the value at infinity,
\\ i.e. coordinates on e_0 = 1, u_a = z^-a, v_b = (z-1)^-b.  For the conjectured vertex r (0 <= r <= n-1) the column set
\\ is e_0, u_1..u_(r+1), v_1..v_(2n-2-r) (the complete system L((r+1)[0] + (2n-2-r)[1])).
\\ Question: is the lowest monomial of that minor lambda^(r(r+1)) lambda'^((n-r)(n-1-r)), and what is its coefficient as a
\\ polynomial in the shapes?  Exact over Q, series in lambda, lambda' truncated at total degree TR.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
al(a) = (-1)^a * binomial(1/2, a);
\\ coordinates of z^-a (z-1)^-b on e_0, u_1.., v_1.. : partial fractions via residues
pf(a, b, A, B) = {
  my(f = 'z^(-a) * ('z - 1)^(-b), c = vector(1 + A + B));
  \\ value at infinity
  c[1] = if (a + b == 0, 1, 0);
  \\ principal part at 0: coefficient of z^-i is the coefficient of z^(a-i) in (z-1)^(-b)
  for (i = 1, A, if (i <= a, c[1 + i] = polcoef(('z - 1)^(-b) + O('z^(a + 1)), a - i, 'z)));
  for (j = 1, B, if (j <= b, c[1 + A + j] = polcoef(subst('z^(-a), 'z, 1 + 'q) + O('q^(b + 1)), b - j, 'q)));
  c;
}
hk(k, v) = polcoef(1 / prod(i = 1, #v, 1 - v[i] * 'T) + O('T^(k + 1)), k, 'T);
vertexminor(n, r, TR) = {
  my(A = r + 1, B = 2 * n - 2 - r, sp = vector(n, j, if (j == 1, 0, if (j == 2, 1, eval(Str("s", j))))));
  my(M = matrix(2 * n, 1 + A + B), row = 0);
  for (l = 0, n - 1, row++;
    for (b = l, l + TR, my(co = al(b) * 'L2^(b - l) * hk(b - l, sp[1..l + 1]));
      M[row, ] += co * pf(0, b, A, B)));
  for (l = 0, n - 1, row++;
    for (a = 1, 1 + TR, for (b = l, l + TR, if ((a - 1) + (b - l) <= TR,
      my(co = al(a) * 'L1^(a - 1) * al(b) * 'L2^(b - l) * hk(b - l, sp[1..l + 1]));
      M[row, ] += co * pf(a, b, A, B)))));
  matdet(M);
}
lowest(D) = {
  \\ lowest monomials in L1, L2 (Newton polygon lower-left): return list of [i, j, coefficient] minimal in i + j and the term at the predicted exponent
  my(best = List(), mn = 10^9);
  for (i = 0, poldegree(D, 'L1), my(Ci = polcoef(D, i, 'L1));
    for (j = 0, poldegree(Ci, 'L2), my(c = polcoef(Ci, j, 'L2)); if (c != 0, listput(best, [i, j, c]))));
  best;
}
main() = {
  for (n = 2, 4, for (r = 0, n - 1,
    my(TR = 2 * n + 2, D = vertexminor(n, r, TR), pi = r * (r + 1), pj = (n - r) * (n - 1 - r), L = lowest(D));
    my(pred = polcoef(polcoef(D, pi, 'L1), pj, 'L2));
    my(below = select(x -> x[1] <= pi && x[2] <= pj && (x[1] < pi || x[2] < pj), Vec(L)));
    my(sp = vector(n, j, if (j == 1, 0, if (j == 2, 1, eval(Str("s", j))))), k = n - r);
    my(H = matdet(matrix(k, k, i, j, sum(q = 1, n, sp[q]^(i + j - 2)))), ratio = pred / H);
    emit(Str("(2,", n, ") r=", r, ": predicted vertex (", pi, ",", pj, "), coefficient ", factor(pred), "; terms at or below it in both coordinates: ", #below,
      "; coefficient / Hankel H_", k, "(power sums of the shape) = ", ratio, (if (type(simplify(ratio)) == "t_INT" || type(simplify(ratio)) == "t_FRAC", " (constant)", " (NOT constant)"))))));
}
main();
