\\ p-adic Newton polygons of the far polynomials (3 October 2026; cycle bmd-20261003-l)
\\ Question (Schur/Filaseta route to irreducibility, hence squarefreeness in characteristic 0): does R_(n,k)
\\ (lem:cube-far-u-space), or R_(n,k)(w) after w -> 1 - w or w -> 1/w, have at some prime p a Newton polygon that
\\ certifies irreducibility (Eisenstein-Dumas: one segment whose slope has denominator deg R), or all segment
\\ lengths forcing it?  Prints, for p <= deg R + 2, the Newton polygon slopes and lengths of R, R(1-w) and w^d R(1/w),
\\ and flags Dumas certificates.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
read("research/tools/bmd_cube_far_modp_specialization.gp");
\\ newton polygon: newtonpoly(x, p) gives slopes (as -valuations increments) per root
dumas(Q, p) = { my(S = newtonpoly(Q, p), d = poldegree(Q)); if (#S == 0, return(0)); my(s = S[1]); for (i = 2, #S, if (S[i] != s, return(0))); denominator(s) == d; }
segs(Q, p) = { my(S = newtonpoly(Q, p), L = List(), c = 1); for (i = 2, #S + 1, if (i <= #S && S[i] == S[i - 1], c++, listput(L, [S[i - 1], c]); c = 1)); Vec(L); }
main2() = {
  foreach(eval(getenv("CASES")), v, my(R = far(v[1], v[2]), d = poldegree(R));
    my(forms = [["R(w)", R], ["R(1-w)", subst(R, 'w, 1 - 'w)], ["w^d R(1/w)", polrecip(R)]]);
    emit(Str("(n,k)=", v, ": deg ", d));
    foreach(forms, f, my(cert = List());
      forprime(p = 2, d + 2, if (dumas(f[2], p), listput(cert, p)));
      emit(Str("  ", f[1], ": Dumas certificates at p = ", Vec(cert)));
      forprime(p = 2, d + 2, emit(Str("    p=", p, " segments [slope, length]: ", segs(f[2], p))))));
}
main2();
quit
