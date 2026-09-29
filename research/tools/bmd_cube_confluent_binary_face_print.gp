\\ Slope-0 edge of the confluent cluster degeneration, 60-digit printing variant (29 September 2026).
\\ Tested statement (cor:cube-confluent-binary-face): for the one-double-root pair space with far
\\ roots +-1 and a cluster eps*(b, u, u) (u double), N = 5, M = 3, r = 3, the non-branch Wronskian
\\ roots at scale |T| ~ 1 converge as eps -> 0 to the zeros of Q_3, as for a separated cluster.
\\ Full pair space: phi_1 phi_-1; phi_(+-1) phi_(eps b), phi_(+-1) phi_(eps u), phi_(+-1) d_u phi_(eps u);
\\ phi_(eps b) phi_(eps u), phi_(eps b) d_u phi_(eps u), phi_(eps u)^2. Exact numerator over Q.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
\p 60
wronsk(fl) = {
  my(n = #fl, P = matrix(n, n));
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], T) / fl[i][j][1]), p = 1); for (k = 1, n, P[k, i] = p; p = deriv(p, T) + p * L));
  numerator(matdet(P));
}
Qr(n) = { my(a = 1, b = 3*'T, c); if (n == 0, return(a)); for (k = 1, n - 1, c = (2*k+3)*'T*b + k*(k+2)*(1-'T^2)*a; a = b; b = c); b; };
main() = {
  my(b = 2, u = 3, s = [1, -1]);
  foreach ([10^-12], eps,
    my(fl = List());
    listput(fl, [[1 + T, -3/2], [1 - T, -3/2]]);
    foreach (s, sg,
      listput(fl, [[1 + sg * T, -3/2], [1 + b * eps * T, -3/2]]);
      listput(fl, [[1 + sg * T, -3/2], [1 + u * eps * T, -3/2]]);
      listput(fl, [[1 + sg * T, -3/2], [T, 1], [1 + u * eps * T, -5/2]]));
    listput(fl, [[1 + b * eps * T, -3/2], [1 + u * eps * T, -3/2]]);
    listput(fl, [[1 + b * eps * T, -3/2], [T, 1], [1 + u * eps * T, -5/2]]);
    listput(fl, [[1 + u * eps * T, -3]]);
    my(q = wronsk(Vec(fl)));
    foreach ([-1, 1, -1 / (b * eps), -1 / (u * eps)], c, while (subst(q, T, c) == 0, q = q / (T - c)));
    my(r = polroots(q), near = [z | z <- Vec(r), abs(z) < 10]);
    my(q3 = polroots(Qr(3)), dist = vector(#q3, i, vecmin(vector(#near, j, abs(near[j] - q3[i])))));
    emit(Str("confluent near roots ", near, " Q3 zeros ", q3)); emit(Str("eps=", eps, ": non-branch degree ", poldegree(q), ", roots at scale 1: ", #near,
      ", max distance of the zeros of Q_3 to them: ", vecmax(dist))));
}
main();
