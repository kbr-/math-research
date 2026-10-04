\\ Route review (cycle kep, 9 October 2026): cheap tests of the review's sign and minor leads on the triple window U_3
\\ (normalization of bmd_triple_window_torus_test.gp, lem:cube-level-window-gegenbauer-form), m = 8..12.
\\ (TP) total positivity: in the real chambers a1 < a2 < a3 < 0 and a1 < 0 < a2 < a3, is the sign of each of the ten
\\      3 x 3 minors constant over 25 random points?  (Constant signs on a chamber are what a total-positivity proof needs.)
\\ (CH) Chebyshev: the consecutive minor {1,2,3} is the sufficient single condition; is its sign constant there?
\\ (MDS) at 25 random complex points, are all ten minors nonzero (normalized size above 1e-40)?
\\ (OSC) Sturm oscillation: sign changes of each pair row's sequence over 200 indices from the window, real chambers.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 80);
lam = 3/2;
rowseq(a, m, r, len) = {
  my(d = m * (m - 1) / 2, N0 = d + m, top = N0 + len, prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]], [i, j, k] = prs[r]);
  my(rho = vector(top + 1, t, exp(lngamma(t) - lngamma(t + lam + m))));
  my(e = Vec(((1 + a[i] * 'T + O('T^(top + 1))) * (1 + a[j] * 'T))^(-lam)));
  vector(len, col, my(n = N0 + col - 1); sum(l = 0, m, binomial(m, l) * a[k]^l * if(n - l >= 0, rho[n - l + 1] * e[n - l + 1], 0)));
}
U3(a, m) = matrix(3, 5, r, c, rowseq(a, m, r, 5)[c]);
minors(U) = { my(L = List()); forsubset([5, 3], S, my(Sv = Vec(S)); listput(L, matdet(matrix(3, 3, r, t, U[r, Sv[t]])))); Vec(L); }
nrm(U) = prod(r = 1, 3, sqrt(norml2(U[r, ])));
rnd() = random(10^6) / 10^6;
{
  setrand(20261009);
  my(ch = [["a1<a2<a3<0", () -> vecsort(-[0.2 + 3 * rnd(), 0.2 + 3 * rnd(), 0.2 + 3 * rnd()])], ["a1<0<a2<a3", () -> concat(-(0.2 + 3 * rnd()), vecsort([0.2 + 3 * rnd(), 0.2 + 3 * rnd()]))]]);
  for(m = 8, 12,
    foreach(ch, C, my(sg = List(), osc = vector(3));
      for(t = 1, 25, my(a = C[2](), U = U3(a, m)); listput(sg, apply(x -> sign(x), minors(U)));
        if(t == 1, for(r = 1, 3, my(s = rowseq(a, m, r, 200)); osc[r] = sum(i = 1, 199, s[i] * s[i + 1] < 0))));
      my(cst = vector(10, j, #Set(vector(25, t, sg[t][j])) == 1));
      emit(Str("m=", m, " chamber ", C[1], ": minors with constant sign over 25 points: ", cst, " (minor {1,2,3} first); sign changes of the three rows over 200 indices at one point: ", osc)));
    my(bad = 0, small = 1.);
    for(t = 1, 25, my(a = [2 * rnd() - 1 + I * (2 * rnd() - 1), 2 * rnd() - 1 + I * (2 * rnd() - 1), 1], U = U3(a, m), v = vecmin(apply(abs, minors(U))) / nrm(U));
      small = min(small, v); if(v < 1e-40, bad++));
    emit(Str("m=", m, " complex points: points with a vanishing minor ", bad, " of 25; least normalized minor ", small)));
}
quit;
