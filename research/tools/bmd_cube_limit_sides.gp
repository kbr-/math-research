\\ Restrictions of the limit determinant Delta_U to the collision lines of the a-plane (bmd-r136).
\\
\\ Statement examined.  The quadrangle route to conj:cube-limit-determinant-squarefree needs, on each of the six
\\ collision lines (triple sides a_j = 0, double-double sides a_i = a_j), the leading coefficient of Delta_U along the
\\ line to be a power of the side's diagonal form times a squarefree part.  U_d = V_nu, nu_r = d - |r| (clipped at
\\ -1), on three variables a = (a1, a2, a3), w_i = (1 + a_i T)^(1/2).  For each d the script computes Delta_U along
\\     triple side:        a = (x, 1, eps),
\\     double-double side: a = (1 + eps, x, 1)   (the side a1 = a3),
\\ exactly over Q[x][eps], takes the lowest nonzero eps-coefficient, and factors it over Q.
\\ Usage: a driver file setting DS=[...]; then read("research/tools/bmd_cube_limit_sides.gp"); quit;
\\ run as gp -q -s 2000000000 DRIVER (the stack cannot be enlarged from inside a read file).
sqser(a, N) = vector(N, k, binomial(1/2, k - 1) * a^(k - 1));
smul(p, q, N) = vector(N, c, sum(i = 1, c, p[i] * q[c - i + 1]));
deltaU(d, a) = {
  my(nu = List(), N, rows = List(), w);
  forvec(r = vector(3, i, [0, 1]), my(v = d - vecsum(r)); if (v >= 0, listput(nu, [r, v])));
  N = sum(i = 1, #nu, nu[i][2] + 1);
  for (i = 1, #nu,
    my(r = nu[i][1]); w = vector(N, k, k == 1);
    for (j = 1, 3, if (r[j], w = smul(w, sqser(a[j], N), N)));
    for (q = 0, nu[i][2], listput(rows, vector(N, k, if (k <= q, 0, w[k - q])))));
  matdet(matrix(N, N, i, j, rows[i][j]));
}
lead(D) = { my(v = valuation(D, 'e)); [v, polcoeff(D, v, 'e)] };
{
  for (t = 1, #DS, my(d = DS[t], Dt, Dd, Lt, Ld);
    Dt = deltaU(d, ['x, 1, 'e]); Lt = lead(Dt);
    print("d=", d, " triple side a=(x,1,eps): eps-valuation ", Lt[1], ", leading coefficient factors ", factor(Lt[2]));
    Dd = deltaU(d, [1 + 'e, 'x, 1]); Ld = lead(Dd);
    print("d=", d, " double-double side a=(1+eps,x,1): eps-valuation ", Ld[1], ", leading coefficient factors ", factor(Ld[2])));
}
