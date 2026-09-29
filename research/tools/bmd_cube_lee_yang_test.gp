\\ Lee-Yang bridge test (30 September 2026; route review bmd-20260930-s).
\\ Tested translation: after some Moebius change of coordinate, the finite non-branch Weierstrass points
\\ of the degree-two pair space at a real configuration lie on one circle (as Lee-Yang zeros do), which
\\ would make them simple by a circle-theorem argument. Test: at real configurations for N = 5 and 6,
\\ compute the roots of W_a(z) numerically (W exact over Q, roots by polroots at high precision) and
\\ check concyclicity: the circle (or line) through three roots and the largest deviation of the
\\ others. A single configuration with deviation far above the precision falsifies the translation
\\ in its simplest form (one circle for all non-branch points).
default(realprecision, 80);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta32(m) = binomial(-3/2, m);
Hk(k, x, y) = sum(m = 0, k, beta32(m) * beta32(k - m) * x^m * y^(k - m));
prs(N) = my(v = List()); for (i = 1, N, for (j = i + 1, N, listput(v, [i, j]))); Vec(v);
Fb(b) = {
  my(N = #b, P = prs(N), R = #P);
  matdet(matrix(R, R, r, k, Hk(k - 1, b[P[r][1]], b[P[r][2]]))) / prod(r = 1, R, (b[P[r][1]] - b[P[r][2]])^(N - 2));
}
Wpoly(a) = {
  my(N = #a, lam = 3 * binomial(N, 4), th = 4 * lam / N, zs = vector(2 * lam + 1, h, h + 1/3));
  polinterpolate(zs, vector(#zs, h, Fb(vector(N, i, 1/(a[i] - zs[h]))) * prod(i = 1, N, a[i] - zs[h])^th), 'z);
}
\\ circle through z1, z2, z3: center c with |c - zi| equal; deviation of |c - z| from the radius
concyc(r) = {
  my(z1 = r[1], z2 = r[2], z3 = r[3]);
  my(A = [real(z2 - z1), imag(z2 - z1); real(z3 - z1), imag(z3 - z1)]);
  my(rhs = [(norm(z2) - norm(z1)) / 2; (norm(z3) - norm(z1)) / 2]);
  if (abs(matdet(A)) < 1e-40, return("collinear first three"));
  my(c = matsolve(A, rhs), cc = c[1] + I * c[2], rad = abs(z1 - cc));
  vecmax(vector(#r, j, abs(abs(r[j] - cc) - rad))) / rad;
}
{
foreach ([[-2, -1, 1/2, 3/2, 3], [-3, -1, 0, 2, 5], [-2, -1, 1/2, 3/2, 3, 7]], a,
  my(w = Wpoly(a), r = polroots(w));
  emit(Str("N=", #a, " a=", a, ": deg W = ", poldegree(w), ", real roots ", #select(x -> abs(imag(x)) < 1e-40, r),
    ", relative deviation from the circle through three roots: ", concyc(r))));
}
