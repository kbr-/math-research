\\ Directional limit of the two-double-root pair block (29 September 2026).
\\ Tested statement: for an exact double root A and B, B+h -> B, the limit as eta -> 0 of
\\ V(eta) = <phi_A, phi_A'> . <phi_B, phi_(B+eta)> (phi_x = (1+xT)^(-3/2), ' = d/dx) is
\\ V7 = (1+AT)^(-5/2) (1+BT)^(-7/2) Pol_(<=3); the mirror limit (A, A+delta; B exact) is
\\ (1+AT)^(-7/2) (1+BT)^(-5/2) Pol_(<=3); the naive span S0 = (1+AT)^(-5/2)(1+BT)^(-5/2) Pol_(<=2).
\\ Method: Taylor jets at T = 0 of length J, all 4 x 4 Pluecker minors as polynomials in eta; the
\\ leading nonzero eta-coefficient vector is the limit's Pluecker vector, compared with V7's.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
J = 9;
jet(f) = vector(J, n, polcoeff(f + O(T^J), n - 1, T));
pw(c, e) = (1 + c * T + O(T^J))^e;
pl(rows) = { my(M = matrix(4, J, i, j, rows[i][j]), out = List()); forsubset([J, 4], s, listput(out, matdet(matrix(4, 4, i, j, M[i, s[j]])))); Vec(out); }
lead(v) = { my(m = vecmin(vector(#v, i, if (v[i] == 0, oo, valuation(v[i], 'h))))); [m, vector(#v, i, polcoeff(v[i], m, 'h))]; }
prop(a, b) = matrank(Mat([a~, b~])) == 1;
main() = {
  my(A = 1, B = 2);
  my(phiA = pw(A, -3/2), dA = -3/2 * T * pw(A, -5/2), phiB = pw(B, -3/2), phiBe = pw(B + 'h, -3/2));
  my(lim = lead(pl([jet(phiA * phiB), jet(dA * phiB), jet(phiA * phiBe), jet(dA * phiBe)])));
  my(V7 = pl(vector(4, k, jet(pw(A, -5/2) * pw(B, -7/2) * T^(k - 1)))));
  my(S0x = pl(concat(vector(3, k, jet(pw(A, -5/2) * pw(B, -5/2) * T^(k - 1))), [jet(pw(A, -5/2) * pw(B, -7/2) * T^3)])));
  emit(Str("A exact: minimal eta-valuation of the Pluecker vector ", lim[1], "; limit = V7: ", prop(lim[2], V7)));
  my(dAe = -3/2 * T * pw(A + 'h, -5/2), phiAe = pw(A + 'h, -3/2), dB = -3/2 * T * pw(B, -5/2));
  my(lim2 = lead(pl([jet(phiA * phiB), jet(phiA * dB), jet(phiAe * phiB), jet(phiAe * dB)])));
  my(V7m = pl(vector(4, k, jet(pw(A, -7/2) * pw(B, -5/2) * T^(k - 1)))));
  emit(Str("B exact (mirror): minimal valuation ", lim2[1], "; limit = mirror V7: ", prop(lim2[2], V7m), "; the two limits equal: ", prop(lim[2], lim2[2])));
  emit(Str("naive derivative rows: rank of the 4 jets ", matrank(Mat([jet(phiA*phiB), jet(dA*phiB), jet(phiA*(-3/2*T*pw(B,-5/2))), jet(dA*(-3/2*T*pw(B,-5/2)))]~))));
}
main();
