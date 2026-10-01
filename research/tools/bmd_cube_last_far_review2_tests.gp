\\ Cheap tests of the second far-input route review (3 October 2026; cycle bmd-20261003-zs), on the saved last-step far
\\ polynomials W_e = W_(b-1), e = 1, 2, 3 (research/results/bmd-20261003-zl/W_last_e*.gp).
\\ (a) Coleman-Filaseta local degrees: the degrees of the irreducible factors of W_e over Q_p at each window prime
\\     (max(d,2n) < p <= 2n+8e+7) and at primes p < 100; the set of degrees t, 0 < t < m, that are subset sums of the local
\\     degrees at every prime tested.  If the set is empty, W_e is irreducible over Q (hence squarefree) by local data alone.
\\ (b) Hirota/Toda recurrence in e: is W_1 W_3 = A W_2^2 + B W_2 W_2' + C W_2'^2 + E W_2 W_2'' with polynomials A, B, C, E of
\\     degree <= deg(W_1 W_3) - 2 deg W_2 + 2?  (Overdetermined: the unknown and equation counts are printed.)
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
subsums(v) = { my(S = Set([0])); foreach (v, a, S = setunion(S, Set(apply(s -> s + a, S)))); S; }
{
for (e = 2, 3,
  my(W = read(Str("research/results/bmd-20261003-zl/W_last_e", e, ".gp")), m = poldegree(W), n = Rn(e), d = Rn(e + 2), ok = Set([1..m-1]), used = List());
  forprime (p = 3, 2 * n + 8 * e + 7,
    if (pollead(W) % p == 0 || poldisc(W) % p == 0 && !(p > max(d, 2 * n)), next);
    my(F = factorpadic(W, p, 30), degs = vector(#F~, i, poldegree(F[i, 1]) * F[i, 2]));
    ok = setintersect(ok, subsums(degs)); listput(used, [p, vecsort(degs)]));
  emit(Str("e=", e, ": deg ", m, "; local factor degrees ", Vec(used)));
  emit(Str("  degrees 0 < t < m compatible with every prime: ", if (#ok, Vec(ok), "none (irreducible from local data)"))));
my(W1 = read("research/results/bmd-20261003-zl/W_last_e1.gp"), W2 = read("research/results/bmd-20261003-zl/W_last_e2.gp"), W3 = read("research/results/bmd-20261003-zl/W_last_e3.gp"));
my(L = W1 * W3, D = poldegree(L) - 2 * poldegree(W2) + 2, basis = [W2^2, W2 * W2', W2'^2, W2 * W2''], cols = List());
foreach (basis, B, for (j = 0, D, listput(cols, B * 'x^j)));
my(N = poldegree(L) + 3, M = matrix(N, #cols, i, c, polcoef(cols[c], i - 1)), v = vector(N, i, polcoef(L, i - 1))~);
my(sol = iferr(matsolve(M~ * M, M~ * v), E, 0), res = if (sol == 0, -1, M * sol - v));
emit(Str("Hirota test: unknowns ", #cols, ", equations ", N, ", exact solution: ", if (sol != 0 && res == 0, "YES", "no"),
  ", rank ", matrank(M), ", rank with W1 W3 appended ", matrank(concat(M, v))));
}
