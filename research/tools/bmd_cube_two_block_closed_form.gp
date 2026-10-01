\\ Closed form of equal-exponent two-block Wronskians (3 October 2026; cycle bmd-20261003-zzt).
\\ Tested statement (lem:two-block-wronskian): for a not an integer and all p, q,
\\   W(x^a P_<p (+) (1+x)^a P_<q) = c x^(pa-pq) (1+x)^(qa-pq) R(x),  R(0) = 1,  R(-1) != 0,  deg R = min(p,q)|p-q|,
\\   c = s * sf(p) sf(q) prod_{i<p, j<q} (a+i-j),  s = +-1,  sf(m) = prod_{i<m} i!,
\\ so for p = q, W = c (x(1+x))^(p(a-p)). Exact check over Q for p, q <= 5 and several a (including a = -n - 7/2), and
\\ (both orders p, q <= 5; strict polynomial test) and of the auxiliary determinant det[(i+q)!/(i+s)!]_{i<q, 1<=s<=q} = +- sf(q).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
ff(a, r) = prod(s = 0, r - 1, a - s);
sf(m) = prod(i = 0, m - 1, i!);
{
my(bad = 0, cnt = 0);
foreach ([-47/2, -61/2, 1/3, -7/2 - 40, 5/2, -2/7], a,
  for (p = 1, 5, for (q = 1, 5,
    my(K = p + q, M = matrix(K, K, r, c, if (c <= p, ff(a + c - 1, r - 1) * x^(c - r), ff(a + c - p - 1, r - 1) * (1 + x)^(c - p - r))));
    \\ D = W / (x^(pa) (1+x)^(qa)) (the pulled factors); predicted D = c x^(-pq) (1+x)^(-pq) R
    my(D = matdet(M) * x^(p * q) * (1 + x)^(p * q), R = D / subst(D, x, 0), cc = subst(D, x, 0), pred = sf(p) * sf(q) * prod(i = 0, p - 1, prod(j = 0, q - 1, a + i - j)));
    cnt++;
    if (!(type(R) == "t_POL" || type(R) == "t_INT" || type(R) == "t_FRAC") || subst(R, x, -1) == 0, bad++; emit(Str("not a polynomial prime to 1+x at a=", a, " p=", p, " q=", q)); next);
    if (poldegree(R) != min(p, q) * abs(p - q) || abs(cc) != abs(pred), bad++; emit(Str("mismatch a=", a, " p=", p, " q=", q, ": deg R ", poldegree(R), " vs ", min(p, q) * abs(p - q), ", |c| ", abs(cc), " vs ", abs(pred)))))));
emit(Str("two-block closed form: ", cnt, " cases (6 values of a, 1 <= p, q <= 5), mismatches ", bad));
my(bad2 = 0);
for (q = 1, 12, if (abs(matdet(matrix(q, q, i, s, (i - 1 + q)! / (i - 1 + s)!))) != sf(q), bad2++));
emit(Str("det[(i+q)!/(i+s)!] = +- sf(q) for q <= 12: mismatches ", bad2));
}
