\\ The triple-side 8-nomial in closed form, checked against the Wronskian of the dual series (bmd-r134).
\\
\\ Statement checked.  lem:cube-triple-side-closed-form: for nu'_d = (2d, 2d-2, 2d-2, 2d-4), n = 2d - 1 and D = 8d,
\\ W(S)/mu^(8d-4) = c_d F_n(t) with t = mu^4 and c_d = +-48 (D-1)(D-2)(D-3)(D-5), where
\\     F_n(t) = 1 + t^(3n) - t^(n-1) q(t) - t^(2n-1) q*(t),  q(t) = A - B t + C t^2,  q*(t) = C - B t + A t^2,
\\     A = n(2n-1), B = 4n^2 - 1, C = n(2n+1)   (so q(1) = 1).
\\ For d = 2..DMAX this script checks F_n against the Wronskian computed by bmd_cube_conic_dual.gp, and prints the
\\ moduli of the roots of Q_d = F_n/((t-1)^6 (t+1)) sorted, grouped by |t| < 1 - 1e-9, |t| ~ 1, |t| > 1 + 1e-9, and the
\\ minimal distance between roots (floating point, 60 digits), to see the three families (inner, unit circle, outer).
\\ Usage: a driver file setting DMAX=...; then read("research/tools/bmd_cube_triple_side_closed.gp"); quit;
NUS = []; TRIPLEMAX = 0;
read("research/tools/bmd_cube_conic_dual.gp");
Fn(n) = { my(A = n*(2*n-1), B = 4*n^2-1, C = n*(2*n+1));
  1 + 't^(3*n) - 't^(n-1) * (A - B*'t + C*'t^2) - 't^(2*n-1) * (C - B*'t + A*'t^2) };
{
  default(realprecision, 60);
  for (d = 2, DMAX,
    my(n = 2*d - 1, S = dualS([2*d, 2*d-2, 2*d-2, 2*d-4])[2], W, Wt, F = Fn(n), ratio, Q, rts, inner = 0, circ = 0, outer = 0, md = oo);
    W = wr(S); W = W / 'm^valuation(W, 'm); Wt = substpol(W, 'm^4, 't);
    ratio = Wt / F;
    Q = F / ('t - 1)^6 / ('t + 1);
    rts = polroots(Q);
    for (i = 1, #rts, my(a = abs(rts[i])); if (a < 1 - 1e-9, inner++, if (a > 1 + 1e-9, outer++, circ++)));
    for (i = 1, #rts, for (j = i + 1, #rts, md = min(md, abs(rts[i] - rts[j]))));
    my(DD = 8*d, want = 48*(DD-1)*(DD-2)*(DD-3)*(DD-5), ord1, R, u2);
    \\ exact: order of F_n at t = 1, Q_d(1), Q_d(-1), and the unit-circle zeros of Q_d via u = t + 1/t on (-2, 2)
    ord1 = valuation(subst(F, 't, 't + 1), 't);
    R = 0; my(QQ = Q, k = poldegree(Q) / 2); forstep(j = k, 0, -1, my(cc = polcoeff(QQ, k + j)); R += cc * 'u^j; QQ -= cc * ('t^2 + 1)^j * 't^(k - j));
    if (QQ != 0, error("Q_d not palindromic of even degree"));
    u2 = polsturm(R, [-2, 2]) - (subst(R, 'u, 2) == 0) - (subst(R, 'u, -2) == 0);
    print("d=", d, " n=", n, ": W/mu^(8d-4) / F_n = ", ratio, " (= 48(D-1)(D-2)(D-3)(D-5): ", ratio == want, ")",
          "; exact: ord_{t=1} F_n = ", ord1, ", Q_d(1) != 0: ", subst(Q, 't, 1) != 0, ", Q_d(-1) != 0: ", subst(Q, 't, -1) != 0,
          ", unit-circle zeros of Q_d (Sturm in u, open arc) = ", 2 * u2,
          "; floating point: deg ", poldegree(Q), ", inner/unit/outer = ", inner, "/", circ, "/", outer, ", min |r_i - r_j| = ", precision(md, 5)));
}
