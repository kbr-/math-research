\\ Base of the confluent three-root shape (8 October 2026; cycle bmd-20261008-zf).
\\ Bottom component carrying the node up, the double root A and two simple roots, normalized A = 0, a_rho = c, a_l = 1.
\\ Confluent pair rows (working context, confluent pair fibre): f_(c,1) = ((1+cT)(1+T))^(-3/2); for each simple root b:
\\ f_(A,b) = (1+bT)^(-3/2) and its partner T (1+AT)^(-5/2) (1+bT)^(-3/2) = T (1+bT)^(-3/2); and (1+AT)^(-3) = 1.
\\ R = 6 rows, columns 0..R+1 = 0..7.  Prints the gcd over Q[c] of the 6 x 6 minors on columns 0..7, on 0..6 and on
\\ 0..5 (factorized): full rank off its roots.  Also the same with A placed at 1 and the simple roots at 0 and c (a
\\ different normalization of the same component), as a control.
default(seriesprecision, 40);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
ser(f, K) = vector(K + 1, k, polcoef(f + O('x^(K + 1)), k - 1, 'x));
rowsfor(A, b1, b2, K) = {
  my(L = List(), p = (u, v) -> ser(((1 + u * 'x + O('x^(K + 1))) * (1 + v * 'x))^(-3/2), K));
  listput(L, p(b1, b2));
  foreach([b1, b2], b, listput(L, p(A, b)); listput(L, ser('x * (1 + A * 'x + O('x^(K + 1)))^(-5/2) * (1 + b * 'x)^(-3/2), K)));
  listput(L, ser((1 + A * 'x + O('x^(K + 1)))^(-3), K));
  matrix(6, K + 1, i, j, L[i][j]);
}
gcdminors(P, cols) = { my(g = 0); forsubset([#cols, 6], S, g = gcd(g, matdet(vecextract(P, "..", vecextract(cols, Vec(S)))))); g; }
{
foreach([["A = 0, roots c, 1", [0, 'c, 1]], ["A = 1, roots 0, c", [1, 0, 'c]]], C,
  my(P = rowsfor(C[2][1], C[2][2], C[2][3], 7));
  foreach([7, 6, 5], top, emit(Str(C[1], ": gcd of 6 x 6 minors on columns 0..", top, ": ", factor(gcdminors(P, [1 .. top + 1]))))));
\\ The least nonzero minor (the invariant (H) of the base): {0..5} off its roots, else {0..4,6}.
my(P = rowsfor(0, 'c, 1, 7), d5 = matdet(vecextract(P, "..", [1 .. 6])), d6 = matdet(vecextract(P, "..", [1, 2, 3, 4, 5, 7])));
emit(Str("A = 0, roots c, 1: minor {0..5} = ", factor(d5), "; minor {0..4,6} = ", factor(d6), "; at c = -1: ", subst(d6, 'c, -1)));
}
quit
