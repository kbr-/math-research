\\ Identify the repeated six-root discriminant factor with the involution locus.
\\
\\ Tested statement: along the line a_i(u) = alpha_i + u beta_i over F_p (p = 2^61 - 1) used by
\\ bmd_cube_wronskian_discriminant.c at N = 6, the monic exponent-four factor G of the
\\ non-collision Wronskian discriminant equals the monic form of
\\     J(u) = prod over the 15 perfect matchings {ij,kl,mn} of
\\            det [1, a_i+a_j, a_i a_j; 1, a_k+a_l, a_k a_l; 1, a_m+a_n, a_m a_n],
\\ whose vanishing says that the three pairs are orbits of one Moebius involution.
\\ Input: a file defining alpha, beta (vectors of integers) and G (polynomial in u).
\\ Usage: gp -q DATA.gp bmd_cube_involution_factor.gp
p = 2^61 - 1;
a = vector(6, i, Mod(alpha[i], p) + Mod(beta[i], p) * 'u);
matchings(S) = {
  my(res = List(), f, rest);
  if (#S == 0, return([[]]));
  f = S[1];
  for (t = 2, #S,
    rest = vector(#S - 2); my(c = 0);
    for (s = 2, #S, if (s != t, c++; rest[c] = S[s]));
    foreach(matchings(rest), m, listput(res, concat([[f, S[t]]], m))));
  Vec(res);
}
M = matchings([1, 2, 3, 4, 5, 6]);
pairrow(i, j) = [1, a[i] + a[j], a[i] * a[j]];
matchdet(m) = matdet(matrix(3, 3, x, y, pairrow(m[x][1], m[x][2])[y]));
J = prod(r = 1, #M, matchdet(M[r]));
Jm = J / pollead(J);
Gm = Mod(1, p) * G;
Gm = Gm / pollead(Gm);
print("matchings=", #M, " degJ=", poldegree(J), " degG=", poldegree(Gm));
print("J monic equals G: ", Jm == Gm);
print("gcd degree: ", poldegree(gcd(Jm, Gm)));
\\ Second comparison: the boundary polynomial F(a(u)) = det(H_k(a_i,a_j)) / prod(a_i-a_j)^4.
beta32(m) = binomial(-3/2, m);
Hk(k, x, y) = sum(m = 0, k, beta32(m) * beta32(k - m) * x^m * y^(k - m));
pairs = vector(15); pc = 0; for (i = 1, 6, for (j = i + 1, 6, pc++; pairs[pc] = [i, j]));
Adet = matdet(matrix(15, 15, r, k, Hk(k - 1, a[pairs[r][1]], a[pairs[r][2]])));
Fu = Adet / prod(r = 1, 15, (a[pairs[r][1]] - a[pairs[r][2]])^4);
Fu = Fu / pollead(Fu);
print("F degree: ", poldegree(Fu), "  F monic equals G: ", Fu == Gm, "  gcd(F,G) degree: ", poldegree(gcd(Fu, Gm)));
\\ Degree pattern of the irreducible factors of G over F_p.
fG = factor(Gm);
print("irreducible factor degrees of G over F_p: ", vecsort(vector(#fG~, k, poldegree(fG[k,1]))));
