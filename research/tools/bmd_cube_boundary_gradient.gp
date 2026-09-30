\\ Gradient of the boundary polynomial at symmetric six-root marks (30 September 2026; cycle bmd-20260930-t).
\\ Tested statement: at a configuration b = (beta1, -beta1, beta2, -beta2, beta3, -beta3) (mark at infinity fixed
\\ by b -> -b, weight three at the mark), is the boundary hypersurface V(F) singular, i.e. grad F(b) = 0?
\\ F(b) = det A_(R-1)(b) / prod_(i<j) (b_i - b_j)^(N-2), R = 15. The partial derivative in b_k is read off from
\\ the polynomial t -> F(b + t e_k), of degree at most (N-1)(R-N+1) = 50 in t (covariant degrees lemma),
\\ interpolated from 53 points (two checks). Control: a random point of V(F) with the other coordinates random
\\ (last coordinate a root of F), where the gradient is expected nonzero.
p = 2^61 - 1;
N = 6; R = 15; DG = (N - 1) * (R - N + 1);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta32(m) = binomial(-3/2, m);
Hk(k, x, y) = sum(m = 0, k, beta32(m) * beta32(k - m) * x^m * y^(k - m));
prs = vector(R); pc = 0; for (i = 1, N, for (j = i + 1, N, pc++; prs[pc] = [i, j]));
Fb(b) = matdet(matrix(R, R, r, k, Hk(k - 1, b[prs[r][1]], b[prs[r][2]]))) / prod(r = 1, R, (b[prs[r][1]] - b[prs[r][2]])^(N - 2));
grad(b) = {
  my(ts = vector(DG + 3, h, Mod(h, p)));
  vector(N, k, my(v = vector(#ts, h, my(c = b); c[k] += ts[h]; Fb(c)));
    my(P = polinterpolate(concat([Mod(0, p)], ts[1..DG]), concat([Fb(b)], v[1..DG]), 't));
    if (subst(P, 't, ts[DG + 1]) != v[DG + 1] || subst(P, 't, ts[DG + 2]) != v[DG + 2], error("interpolation check"));
    polcoef(P, 1, 't));
}
main() = {
  setrand(20260930);
  for (trial = 1, 3,
    my(be = vector(3, i, Mod(random(p), p)), b = [be[1], -be[1], be[2], -be[2], be[3], -be[3]]);
    my(g = grad(b));
    emit(Str("symmetric point ", trial, ": F(b) = ", lift(Fb(b)), ", gradient zero: ", g == vector(N, k, 0),
      ", number of nonzero partials: ", #select(x -> x != 0, g))));
  for (trial = 1, 2,
    my(b0 = vector(N - 1, i, Mod(random(p), p)), f = Fb(concat(b0, ['x])), r = polrootsmod(numerator(f) * Mod(1, p)));
    if (#r == 0, emit("control: no rational root on this fibre"); next);
    my(b = concat(b0, [r[1]]), g = grad(b));
    emit(Str("control point ", trial, ": F(b) = ", lift(Fb(b)), ", gradient zero: ", g == vector(N, k, 0),
      ", number of nonzero partials: ", #select(x -> x != 0, g))));
}
main();
