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
\\ Cycle bmd-20261002-k: the lambda-reduction.  M_r(lambda') has rows B_l: (0 on r+1 extra columns | coordinates of B_l on e_0, v_1..v_B)
\\ and rows A_1 B_l at lambda = 0: (Taylor coefficients rho_(l,0..r) of B_l at 0 | alpha_1 times the coordinates of B_l / z on e_0, v_1..v_B).
\\ Claim: the coefficient of lambda^(r(r+1)) in the vertex minor is C_r det M_r(lambda'), C_r = det(alpha_(i+k))_(1<=i<=r+1, 0<=k<=r).
lamred(n, r, TR, spin = 0) = {
  my(A = r + 1, B = 2 * n - 2 - r, sp = if (spin != 0, spin, vector(n, j, if (j == 1, 0, if (j == 2, 1, eval(Str("s", j)))))));
  my(M = matrix(2 * n, (r + 1) + 1 + B), row = 0);
  for (l = 0, n - 1, row++;
    for (b = l, l + TR, my(co = al(b) * 'L2^(b - l) * hk(b - l, sp[1..l + 1]), c = pf(0, b, 0, B));
      for (q = 1, 1 + B, M[row, r + 1 + q] += co * c[q])));
  for (l = 0, n - 1, row++;
    for (b = l, l + TR, my(co = al(b) * 'L2^(b - l) * hk(b - l, sp[1..l + 1]), c = pf(1, b, 0, B));
      for (k = 0, r, M[row, k + 1] += co * polcoef(('z - 1)^(-b) + O('z^(r + 1)), k, 'z));
      for (q = 1, 1 + B, M[row, r + 1 + q] += al(1) * co * c[q])));
  matdet(M);
}
checkred() = {
  for (n = 2, 4, for (r = 0, n - 1,
    my(TR = 2 * n + 2, D = vertexminor(n, r, TR), Cr = matdet(matrix(r + 1, r + 1, i, k, al(i + k - 1))));
    \\ the u-columns stand before e_0 in M_r and after it in the minor: sign (-1)^(r+1)
    my(lhs = polcoef(D, r * (r + 1), 'L1), rhs = (-1)^(r + 1) * Cr * lamred(n, r, TR), pj = (n - r) * (n - 1 - r), diff = lhs - rhs, low = 1);
    for (j = 0, pj, if (polcoef(diff, j, 'L2) != 0, low = 0));
    \\ only terms of total degree <= TR are exact
    my(lower = 1); for (i = 0, r * (r + 1) - 1, my(Ci = polcoef(D, i, 'L1)); for (j = 0, TR - i, if (polcoef(Ci, j, 'L2) != 0, lower = 0)));
    emit(Str("(2,", n, ") r=", r, ": no lambda-power below r(r+1): ", lower, "; lambda^(r(r+1)) coefficient = C_r det M_r up to lambda'^", pj, ": ", low))));
}
\\ Cycle bmd-20261002-m: the corner Hankel theorem.  Claim: det M_r(lambda') has lambda'-order exactly c(c+1), c = n-1-r,
\\ with coefficient kappa_(n,r) H_(n-r)(s'), kappa_(n,r) a nonzero constant (independent of the shape).  Checked at two random
\\ integer shapes (s'_1 = 0, s'_2 = 1) per (n, r): no lower lambda'-power, and the same nonzero ratio to H_(n-r) at both.
\\ Also checks the proof's final identity det[s_i^j | 0; s_i^(j+1)/(j+1) | s_i^k] = const V(s)^2 H_(c+1)(s).
hankelthm(NMAX) = {
  setrand(20261002);
  for (n = 2, NMAX, for (r = 0, n - 1,
    my(c = n - 1 - r, TR = c * (c + 1), rat = vector(2), low = 1, rid = vector(2));
    for (t = 1, 2,
      my(sp = vector(n, j, if (j == 1, 0, if (j == 2, 1, random(61) - 30))));
      while (#Set(sp) < n, sp = vector(n, j, if (j == 1, 0, if (j == 2, 1, random(61) - 30))));
      my(D = lamred(n, r, TR, sp), H = matdet(matrix(c + 1, c + 1, i, j, sum(q = 1, n, sp[q]^(i + j - 2)))));
      for (j = 0, TR - 1, if (polcoef(D, j, 'L2) != 0, low = 0));
      rat[t] = polcoef(D, TR, 'L2) / H;
      my(B = n + c - 1, N = matrix(2 * n, 2 * n), V = prod(i = 1, n, prod(j = i + 1, n, sp[j] - sp[i])));
      for (i = 1, n, for (j = 0, B, N[i, j + 1] = sp[i]^j; N[n + i, j + 1] = sp[i]^(j + 1) / (j + 1));
        for (k = 0, r, N[n + i, B + 2 + k] = sp[i]^k));
      rid[t] = matdet(N) / (V^2 * H));
    emit(Str("(2,", n, ") r=", r, " c=", c, ": no lambda'-power below c(c+1): ", low, "; coefficient/H_", c + 1, " at two shapes: ",
      rat[1], ", ", rat[2], if (rat[1] == rat[2] && rat[1] != 0, " (equal, nonzero)", " (MISMATCH)"),
      "; initial-matrix identity ratio: ", rid[1], ", ", rid[2], if (rid[1] == rid[2] && rid[1] != 0, " (equal)", " (MISMATCH)")))));
}
MODE = getenv("MODE");
if (MODE == "hankelthm", hankelthm(7), checkred());
