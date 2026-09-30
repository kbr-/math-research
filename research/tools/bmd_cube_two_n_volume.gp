\\ Recurrence determinant of thm:cube-two-n-volume (30 September 2026; cycle bmd-20260930-zy).
\\ For the (2,n) spine class: costs 1: 0, u1^s: 3s-2, u2^m: m (m < n), m+2 (m >= n); the 2n cheapest are selected,
\\ and at a tie at the largest selected cost the u2-monomial is kept (u1 dropped).  With a = number of selected u1^s and
\\ b' = largest selected u2 exponent, E(y) = prod (y - c_k), F = nE - yE', I_m(y) = int_0^y t^(m-n) F(t) dt, the
\\ determinant is D_n = det[ coefficient of y^e in (I_m mod E) ]_(m = n..b', e = a..n-1).  The script prints a, b',
\\ checks b' - n + 1 = n - a and 2(a-1) < n (used in the proof), and evaluates D_n exactly at two rational shape
\\ vectors (a nonzero value proves D_n is not identically zero), for n = 2..NMAX; at n = 3 it also checks D_3 = e_2
\\ symbolically.  It then evaluates D_n at the shapes of the flat-limit runs of two-n-extras.txt / two-n-predict.txt.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
slots(n) = {
  my(L = List([[0, "1", 0]]), C = 4 * n + 10);
  for (s = 1, C, listput(L, [3 * s - 2, "u1", s]));
  for (m = 1, C, listput(L, [if (m < n, m, m + 2), "u2", m]));
  L = vecsort(Vec(L), 1);
  \\ select 2n cheapest; tie at the boundary: keep u2
  my(cstar = L[2 * n][1], below = select(t -> t[1] < cstar, L), at = select(t -> t[1] == cstar, L), need = 2 * n - #below, pick);
  if (#at > need, pick = vecsort(at, t -> if (t[2] == "u2", 0, 1)); pick = pick[1..need], pick = at);
  my(sel = concat(below, pick), a = #select(t -> t[2] == "u1", sel), bb = vecmax(apply(t -> if (t[2] == "u2", t[3], 0), sel)));
  [a, bb, #at > need, cstar];
}
Dn(n, c) = {
  my(E = prod(k = 1, n, 'y - c[k]), F = n * E - 'y * deriv(E, 'y), sab = slots(n), a = sab[1], bb = sab[2]);
  my(rows = vector(bb - n + 1, i, my(m = n + i - 1, I = intformal('y^(m - n) * F, 'y), R = I % E); vector(n - a, j, polcoef(R, a + j - 1, 'y))));
  if (#rows != n - a, error("not square"));
  if (#rows == 0, return(1));
  matdet(Mat(Vec(rows)~));
}
main() = {
  my(NMAX = if (getenv("NMAX"), eval(getenv("NMAX")), 30));
  for (n = 2, NMAX,
    my(sab = slots(n), a = sab[1], bb = sab[2]);
    if (bb - n + 1 != n - a, error(Str("count n=", n)));
    if (2 * (a - 1) >= n, error(Str("Hankel tail condition fails n=", n)));
    my(c1 = vector(n, k, (3 * k^2 + 7 * k + 2) / (5 + k)), c2 = vector(n, k, (-1)^k * (2 * k + 1) / (k^2 + 3)));
    my(d1 = Dn(n, c1), d2 = Dn(n, c2));
    emit(Str("n=", n, ": a=", a, ", b'=", bb, ", tie=", sab[3], ", c*=", sab[4], "; D_n(c1) != 0: ", d1 != 0, "; D_n(c2) != 0: ", d2 != 0)));
  \\ n = 3 symbolic: D_3 = e_2 (up to the order of rows); centred symbolic shapes
  my(c = ['s, 't, -'s - 't], e2 = 's * 't + 's * (-'s - 't) + 't * (-'s - 't));
  emit(Str("n=3 symbolic centred: D_3 / e_2 = ", Dn(3, c) / e2));
  \\ uncentred: compare with e_2 - e_1^2/3 and with the variance sum
  my(cu = ['s, 't, 'w], e1 = 's + 't + 'w, e2u = 's * 't + 's * 'w + 't * 'w, cb = e1 / 3, var = sum(k = 1, 3, (cu[k] - cb)^2));
  emit(Str("n=3 symbolic uncentred: D_3 = e_2 - e_1^2/3: ", Dn(3, cu) == e2u - e1^2 / 3, "; D_3 / sum (c_k - cbar)^2 = ", Dn(3, cu) / var));
  \\ the shapes used in the flat-limit runs (two-n-extras.txt, two-n-predict.txt)
  foreach ([[-1, 1], [-2, 2], [-1, 0, 1], [-3, 1, 2], [-3, -1, 1, 3], [-3, 0, 1, 2], [-2, -1, 0, 1, 2], [-5, -3, -1, 1, 3, 5], [-5, -2, 0, 1, 2, 4], [-3, -2, -1, 0, 1, 2, 3], [-4, -2, -1, 0, 1, 2, 4]], c,
    emit(Str("flat-limit shapes c = ", c, ": D_n != 0: ", Dn(#c, c) != 0)));
}
main();
quit
