\\ Lowest homogeneous parts of the window Pluecker coordinates of a product of two clusters (29 September
\\ 2026; cycle bmd-20260929-za). Rows (1 + s_i/S)^(-3/2)(1 + t_j S)^(-3/2), i <= F, j <= n, with symbolic s, t;
\\ the coefficient of S^e is sum_(b-a=e) beta_a beta_b s_i^a t_j^b, truncated at total degree D. For each
\\ consecutive window W of length F n, prints the factorization of the lowest-degree part of det over W
\\ (in the grading where s and t have degree 1), and its degree. Tested question: do these initial forms
\\ factor into Vandermondes of s and t times Schur-type polynomials, which would give the caterpillar
\\ valuation of every window in closed form?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
be(n) = binomial(-3/2, n);
ent(s, t, ee, D) = sum(a = max(0, -ee), D, my(b = a + ee); if (a + b > D, 0, be(a) * be(b) * s^a * t^b));
lowpart(f, vars) = {
  \\ lowest total degree part in the given variables
  my(h = substpol(f, 'z, 'z), w = f, low = oo, res = 0);
  my(g = subst(subst(subst(subst(f, vars[1], 'h * vars[1]), vars[2], 'h * vars[2]), vars[3], 'h * vars[3]), vars[4], 'h * vars[4]));
  my(v = valuation(g, 'h)); [v, polcoef(g, v, 'h)];
}
run(F, n, D) = {
  my(sv = vector(F, i, eval(Str("s", i))), tv = vector(n, j, eval(Str("t", j))), rows = List());
  foreach (sv, s, foreach (tv, t, listput(rows, s)));
  for (p = F - 1, F * n - n, my(q = F * n - 1 - p);
    my(A = matrix(F * n, F * n, r, c, my(i = (r - 1) \ n + 1, j = (r - 1) % n + 1, ee = c - 1 - p); ent(sv[i], tv[j], ee, D)));
    my(d = matdet(A), vars = concat(sv, tv));
    my(g = d); foreach (vars, x, g = subst(g, x, 'h * x)); my(v = valuation(g, 'h), lp = polcoef(g, v, 'h));
    emit(Str(F, "x", n, " window [", -p, ",", q, "]: lowest degree ", v, "; factorization ", factor(lp))));
}
run(2, 2, 8);
if (getenv("MORE") == "1", run(2, 3, 12); run(3, 2, 12));
