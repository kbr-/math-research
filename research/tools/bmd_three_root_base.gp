\\ Base of the three-root level (8 October 2026; cycle bmd-20261008-v).  The pair matrix of a separated triple of roots,
\\ normalized by translation and dilation to (0, c, 1), c not in {0, 1}: rows H_k(x, y) = [T^k] (1+xT)^(-3/2) (1+yT)^(-3/2)
\\ for the pairs {0,c}, {0,1}, {c,1}, columns k = 0..4 (R = 3, columns 0..R+1).  Prints the gcd over Q[c] of its ten
\\ 3 x 3 minors and its factorization: rank 3 at every c off the roots of that gcd.  Also the same for columns 0..3 only
\\ (the codimension-one locus rank A_R < R) as a control.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));

{
my(K = 4, P, G = 0, G4 = 0);
P = matrix(3, K + 1, i, j, polcoef(((1 + [0, 0, 'c][i] * 'x) * (1 + ['c, 1, 1][i] * 'x))^(-3/2) + O('x^(K + 1)), j - 1, 'x));
forsubset([K + 1, 3], S, G = gcd(G, matdet(vecextract(P, "..", Vec(S)))));
forsubset([4, 3], S, G4 = gcd(G4, matdet(vecextract(P, "..", Vec(S)))));
emit(Str("pair matrix of (0, c, 1) on columns 0..4: gcd of 3 x 3 minors = ", factor(G)));
emit(Str("control, columns 0..3: gcd of 3 x 3 minors = ", factor(G4)));
}
quit
