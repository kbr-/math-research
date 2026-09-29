\\ Direct root count of the half-integral cross-row Wronskian (29 September 2026).
\\ Decides between two predictions for a cluster of M = 3 roots with one double root, eps small:
\\  Newton hull (thm:cube-confluent-neck-hull): 2M(M-2) = 6 neck roots, all at |T| ~ eps^(-1/3),
\\    none at eps^(-2/3), and the rest at the cluster scale eps^(-1);
\\  Eisenbud-Harris exponent count at the node: at least 2M(M-1) = 12 neck roots.
\\ Control: a separated cluster, predicted 6 at eps^(-1/3) and 6 at eps^(-2/3).
\\ Functions: (1+sT)^(-3/2) g(eps T), s = +-1, g in the cluster span: (1+b x)^(-3/2) for simple
\\ roots b, and for the double root u also d/du (1+u x)^(-3/2) ~ x (1+u x)^(-5/2).
\\ The Wronskian is prod f_i times det[P_k^(i)], P_0 = 1, P_(k+1) = P_k' + P_k f_i'/f_i; its
\\ numerator is factored free of the branch factors, and its roots binned by log|T|/log(1/eps).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
\p 600
wronsk_roots(fl) = {
  my(n = #fl, P = matrix(n, n));
  \\ each function is a list of factors [linear polynomial, exponent]; L is its log-derivative
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], T) / fl[i][j][1]), p = 1); for (k = 1, n, P[k, i] = p; p = deriv(p, T) + p * L));
  my(d = matdet(P), num = numerator(d));
  num;
}
bins(num, eps, br) = {
  my(q = num);
  foreach (br, c, while (subst(q, T, c) == 0, q = q / (T - c)));
  my(r = polroots(q), h = Map());
  my(out = vector(#r, i, round(4 * log(abs(r[i])) / log(1 / eps)) / 4));
  my(v = vecsort(out), res = List(), i = 1);
  while (i <= #v, my(j = i); while (j < #v && v[j + 1] == v[i], j++); listput(res, [v[i], j - i + 1]); i = j + 1);
  my(raw = vecsort(vector(#r, i, round(10^4 * log(abs(r[i])) / log(1 / eps)) / 10^4.)));
  [poldegree(q), Vec(res), poldegree(gcd(q, deriv(q))), raw];
}
main() = {
  my(eps = 1 / 10^12, s = [1, -1]);
  \\ separated cluster b = 2, 3, -5
  my(B = [2, 3, -5], fl = List());
  foreach (s, sg, foreach (B, b, listput(fl, [[1 + sg * T, -3/2], [1 + b * eps * T, -3/2]])));
  my(num = wronsk_roots(Vec(fl)));
  emit(Str("separated b=", B, ": [degree, [scale exponent, count], sqfree-defect] = ",
    bins(num, eps, concat([-1, 1], vector(#B, i, -1 / (B[i] * eps))))));
  \\ confluent cluster: simple b = 2, double u = 3
  my(b = 2, u = 3, fl = List());
  foreach (s, sg,
    listput(fl, [[1 + sg * T, -3/2], [1 + b * eps * T, -3/2]]);
    listput(fl, [[1 + sg * T, -3/2], [1 + u * eps * T, -3/2]]);
    listput(fl, [[1 + sg * T, -3/2], [T, 1], [1 + u * eps * T, -5/2]]));
  my(num = wronsk_roots(Vec(fl)));
  emit(Str("confluent b=", b, " u=", u, " (double): ", bins(num, eps, [-1, 1, -1 / (b * eps), -1 / (u * eps)])));
}
main();
