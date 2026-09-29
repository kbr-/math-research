\\ The odd/even ratio of the neck: tau(y) = O/E for E, O the even and odd parts of (1+y)^(-3/2).
\\ Tested statements (exact power series over Q to order 2*NN):
\\ (1) tau(y) = -tanh((3/2) artanh y);
\\ (2) the Gauss continued fraction  tanh(l*artanh y) = l*y / (1 + (l^2-1) y^2 / (3 + (l^2-4) y^2 /
\\     (5 + (l^2-9) y^2 / (7 + ...)))) holds at l = 3/2 to the computed order, with partial numerators
\\     (l^2 - n^2), n = 1..NN-1, all nonzero; hence the odd Hankel determinants of tau are nonzero
\\     (normal odd Pade table), checked directly for sizes 1..NN/2.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
NN = 24;
main() = {
  my(y = 'y + O('y^(2*NN + 2)), u = (1 + y)^(-3/2), v = (1 - y)^(-3/2), E = (u + v) / 2, Od = (u - v) / 2);
  my(tau = Od / E, l = 3/2, th = tanh(l * atanh(y)));
  emit(Str("(1) tau + tanh(3/2 artanh y) = O(y^", 2*NN + 2, "): ", tau + th == 0));
  \\ continued fraction evaluated bottom-up
  my(cf = 2 * NN + 1);
  forstep (n = NN - 1, 1, -1, cf = (2 * n - 1) + (l^2 - n^2) * y^2 / cf);
  my(cfv = l * y / cf);
  emit(Str("(2) continued fraction matches tanh(3/2 artanh y) to order ", 2 * NN - 2, ": ", truncate(cfv - th + O('y^(2*NN - 2))) == 0,
    "; partial numerators l^2-n^2 nonzero for n=1..", NN - 1, ": ", prod(n = 1, NN - 1, l^2 - n^2) != 0));
  \\ Hankel determinants of the odd coefficients t_1, t_3, ...
  my(t = vector(NN, j, polcoeff(truncate(tau), 2 * j - 1, 'y)));
  my(H0 = vector(NN \ 2, n, matdet(matrix(n, n, i, j, t[i + j - 1]))), H1 = vector(NN \ 2 - 1, n, matdet(matrix(n, n, i, j, t[i + j]))));
  emit(Str("    Hankel dets det(t_(2(i+j)-3)) nonzero for n=1..", #H0, ": ", vecmin(apply(x -> x != 0, H0)) == 1,
    "; shifted det(t_(2(i+j)-1)) nonzero for n=1..", #H1, ": ", vecmin(apply(x -> x != 0, H1)) == 1));
}
main();
