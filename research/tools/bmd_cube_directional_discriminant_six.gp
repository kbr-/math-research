\\ The level-two (directional) discriminant at N = 6, completely (30 September 2026).
\\ Space V^(2) (research/tools/bmd_cube_hierarchical_attainment.gp): doubles A = 1 (first),
\\ B = 2 (second, block T^j (1+AT)^(-5/2)(1+BT)^(-7/2)), simple roots -1 and s. Up to Moebius
\\ maps, which act covariantly on the space, every configuration of two ordered doubles and two
\\ simple roots is of this form, so s is a complete parameter (a cross ratio).
\\ Question (falsification test of the discriminant descent): at N = 6 the separated discriminant
\\ has an exponent-four factor (check:cube-wronskian-discriminant-certificates), which the descent
\\ must place in a remainder. Is the level-two discriminant D^dir(s) squarefree away from the
\\ collision and degenerate values s in {-1, 1, 2, 0}?
\\ Method (mod p = 2^61-1): for each s, the cleared numerator P_s(z) (degree <= 226) by
\\ interpolation with two checks; the branch factors (1+z)^41 (1+2z)^37 (1-z)^55 (1+sz)^55
\\ (minimal multiplicities, bmd_cube_directional_two_double.gp) are divided out exactly
\\ (remainder checked), leaving W_s of degree 38 = T_dir(6); D(s) = disc(W_s). D is interpolated
\\ in s with two checks; its squarefree decomposition is reported, with the factors at the
\\ special values separated.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
serpow(u, al, L) = vector(L, m, binomial(al, m - 1) * u^(m - 1));
mul(A, B, L) = vector(L, n, sum(m = 1, n, A[m] * B[n + 1 - m]));
tx(B, t, L) = vector(L, n, t * B[n] + if (n > 1, B[n - 1], 0));
rowsh(Ds, sim, t, L) = {
  my(R = List(), p(c, e) = serpow(c / (1 + c * t), e, L));
  for (i = 1, #sim, for (k = i + 1, #sim, listput(R, mul(p(sim[i], -3/2), p(sim[k], -3/2), L))));
  foreach (Ds, D, foreach (sim, k,
    listput(R, mul(p(D, -3/2), p(k, -3/2), L));
    listput(R, tx(mul(p(D, -5/2), p(k, -3/2), L), t, L))));
  foreach (Ds, D, listput(R, p(D, -3)));
  for (r = 1, #Ds, for (s = r + 1, #Ds,
    my(v = mul(p(Ds[r], -5/2), p(Ds[s], -7/2), L));
    for (j = 0, 3, listput(R, v); v = tx(v, t, L))));
  if (#R != L, error("row count"));
  matrix(L, L, r, j, R[r][j]);
}
Dval(s) = {
  my(Ds = [Mod(1, q), Mod(2, q)], sim = [Mod(-1, q), s], vals = concat(Ds, sim), R = 15, E = 105, DT = 226);
  my(ts = vector(DT + 3, j, Mod(j + 7, q)));
  my(ys = vector(DT + 3, j, matdet(rowsh(Ds, sim, ts[j], R)) * prod(c = 1, 4, (1 + vals[c] * ts[j])^E)));
  my(P = polinterpolate(ts[1..DT + 1], ys[1..DT + 1], 'z));
  if (subst(P, 'z, ts[DT + 2]) != ys[DT + 2] || subst(P, 'z, ts[DT + 3]) != ys[DT + 3], error("z check"));
  my(B = (1 + 'z)^41 * (1 + 2 * 'z)^37 * (1 - 'z)^55 * (1 + s * 'z)^55);
  my(dv = divrem(P, B));
  if (dv[2] != 0, return([0, 0]));
  my(W = dv[1]);
  [poldisc(W), poldegree(W)];
}
export(q, serpow, mul, tx, rowsh, Dval);
main() = {
  my(K = if (getenv("K"), eval(getenv("K")), 6000));
  my(ss = vector(K + 2, i, Mod(i + 10, q)));
  my(V = parvector(K + 2, i, Dval(ss[i])));
  my(bad = select(v -> v[2] != 38, V));
  emit(Str("s-values: ", K + 2, "; values with W degree != 38 or inexact division: ", #bad));
  if (#bad, return);
  my(vals = vector(K + 2, i, V[i][1]));
  my(Dp = polinterpolate(ss[1..K], vals[1..K], 's));
  if (subst(Dp, 's, ss[K + 1]) != vals[K + 1] || subst(Dp, 's, ss[K + 2]) != vals[K + 2], emit("s check failed: raise K"); return);
  emit(Str("deg D(s) = ", poldegree(Dp)));
  my(special = [-1, 1, 2, 0], rest = Dp, mults = vector(4));
  for (c = 1, 4, while (subst(rest, 's, Mod(special[c], q)) == 0, rest = rest \ ('s - special[c]); mults[c]++));
  emit(Str("multiplicities of s = -1, 1, 2, 0: ", mults, "; remaining degree ", poldegree(rest)));
  my(sq = factorsqrfree(rest));
  emit(Str("squarefree decomposition of the rest [multiplicity, degree]: ", apply(v -> [v[2], poldegree(v[1])], sq)));
}
factorsqrfree(f) = {
  my(res = List(), g = f, k = 0);
  \\ Yun's algorithm over F_p (characteristic larger than every degree here)
  my(c = gcd(g, deriv(g)), w = g / c);
  while (poldegree(w) > 0, k++; my(y = gcd(w, c)); my(z = w / y); if (poldegree(z) > 0, listput(res, [z, k])); w = y; c = c / y);
  Vec(res);
}
default(nbthreads, 12);
main();
