\\ Symmetric approach of a double root in the two-double-root pair block (29 September 2026).
\\ Tested statement (proved in the notebook for every A != B): with A exact and B approached
\\ symmetrically by B+h, B-h, the limit as h -> 0 of <phi_A, phi_A'> . <phi_(B+h), phi_(B-h)> is
\\ V7 = (1+AT)^(-5/2) (1+BT)^(-7/2) Pol_(<=3), the fourth function entering at order h^2.
\\ Control: exact Pluecker vectors of 9-term Taylor jets at T = 0, for several (A, B) including B = 0.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
J = 9;
jet(f) = vector(J, n, polcoeff(f + O(T^J), n - 1, T));
pw(c, e) = (1 + c * T + O(T^J))^e;
pl(rows) = { my(M = matrix(4, J, i, j, rows[i][j]), out = List()); forsubset([J, 4], s, listput(out, matdet(matrix(4, 4, i, j, M[i, s[j]])))); Vec(out); }
lead(v) = { my(m = vecmin(vector(#v, i, if (v[i] == 0, oo, valuation(v[i], 'h))))); [m, vector(#v, i, polcoeff(v[i], m, 'h))]; }
prop(a, b) = matrank(Mat([a~, b~])) == 1;
main() = {
  foreach ([[1, 2], [3, -1], [2, 0], [-5, 7]], ab,
    my(A = ab[1], B = ab[2], phiA = pw(A, -3/2), dA = -3/2 * T * pw(A, -5/2));
    my(bp = pw(B + 'h, -3/2), bm = pw(B - 'h, -3/2));
    my(lim = lead(pl([jet(phiA * bp), jet(phiA * bm), jet(dA * bp), jet(dA * bm)])));
    my(V7 = pl(vector(4, k, jet(pw(A, -5/2) * pw(B, -7/2) * T^(k - 1)))));
    emit(Str("A=", A, " B=", B, ": minimal h-valuation ", lim[1], "; limit = V7: ", prop(lim[2], V7))));
}
main();
