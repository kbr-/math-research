\\ Augmented confluent tie windows (7 October 2026; cycle bmd-20261007-zo).
\\ gcd of the maximal minors of W^c(c) divides det[W^c(c); phi_1; phi_2] for any two rows phi_1, phi_2 with polynomial
\\ entries in c (Laplace along the added rows).  If some augmentation has determinant const * c^x (c-1)^y, the special
\\ values Z^W_m lie in {0,1}.  Tests natural augmentations on the 3m+5 window columns T^d..T^(d+3m+4), m = 1..5:
\\   A: T^(2m) (1+T)^(-5/2), T^(2m+1) (1+T)^(-5/2)   (extend the first family)
\\   B: T^m (1+cT)^(-3/2), T^(m+1) (1+cT)^(-3/2)     (extend the second family)
\\   C: T^(2m) (1+T)^(-5/2), T^m (1+cT)^(-3/2)       (one of each)
\\   D: T (1+T)^(-3), T^2 (1+T)^(-3)                 (extend the row (1+T)^(-3))
\\ Prints, for each, whether the determinant is nonzero and the degree of its part prime to c(c-1).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
rowco(r, m, k) = {
  if (r <= 2 * m, return(bn(-5/2, k - (r - 1))));
  if (r <= 3 * m, my(n = r - 2 * m - 1); return(bn(-3/2, k - n) * 'c^max(k - n, 0)));
  if (r == 3 * m + 1, return(bn(-3, k)));
  if (r == 3 * m + 2, return(sum(a = 0, k, bn(-3/2, a) * bn(-3/2, k - a) * 'c^(k - a))));
  sum(a = 0, k - 1, bn(-5/2, a) * bn(-3/2, k - 1 - a) * 'c^(k - 1 - a));
}
fam1(i, k) = bn(-5/2, k - i);
fam2(n, k) = bn(-3/2, k - n) * 'c^max(k - n, 0);
fam3(j, k) = bn(-3, k - j);
\\ run 2 adds E: T ((1+T)(1+cT))^(-3/2), T^2 (1+T)^(-5/2) (1+cT)^(-3/2);  F: T (1+T)^(-3), T ((1+T)(1+cT))^(-3/2);
\\ G: T^m (1+cT)^(-3/2), T ((1+T)(1+cT))^(-3/2)
mixR2(j, k) = if (k < j, 0, sum(a = 0, k - j, bn(-3/2, a) * bn(-3/2, k - j - a) * 'c^(k - j - a)));
mixR3(j, k) = if (k < j, 0, sum(a = 0, k - j, bn(-5/2, a) * bn(-3/2, k - j - a) * 'c^(k - j - a)));
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
{
for (m = 1, 5,
  my(d = m * (m - 1) / 2, w = 3 * m + 5, W = matrix(3 * m + 3, w, r, j, rowco(r, m, d + j - 1)), res = List());
  my(cands = [["A", [k -> fam1(2*m, k), k -> fam1(2*m + 1, k)]], ["B", [k -> fam2(m, k), k -> fam2(m + 1, k)]],
               ["C", [k -> fam1(2*m, k), k -> fam2(m, k)]], ["D", [k -> fam3(1, k), k -> fam3(2, k)]],
               ["E", [k -> mixR2(1, k), k -> mixR3(2, k)]], ["F", [k -> fam3(1, k), k -> mixR2(1, k)]], ["G", [k -> fam2(m, k), k -> mixR2(1, k)]]]);
  foreach(cands, cd, my(F = cd[2], M = matconcat([W; vector(w, j, F[1](d + j - 1)); vector(w, j, F[2](d + j - 1))]), D = matdet(M));
    listput(res, Str(cd[1], ": ", if (D == 0, "zero", Str("c^", valuation(D, 'c), " (c-1)^", valuation(D, 'c - 1), " * degree ", poldegree(strip01(D), 'c))))));
  emit(Str("m = ", m, ": ", Vec(res))));
}
quit
