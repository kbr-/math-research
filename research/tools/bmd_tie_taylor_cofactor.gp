\\ Taylor cofactor at a tie limit (cycle bmd-20261009-ad, 9 October 2026).
\\ For M roots, p_T0(y) = Taylor minor (columns 0..binom(M,2)-1) of the pair span (rows [w^t]((1+y_i w)(1+y_j w))^(-3/2));
\\ every minor is divisible by Vand(y)^(M-2) (prop:cube-minimality-small-clusters), so F = p_T0 / Vand^(M-2).
\\ Computes F(c, 1, 0, ..., 0) as a polynomial in c, via y = (c, 1, e z_3, ..., e z_M) with fixed rational z and
\\ the exact quotient p_T0 / Vand^(M-2), evaluated at e = 0 (F is a polynomial), for M = 3, 4, 5.
\\ Reports its factorization and whether the excluded tie moduli (M-1)c^2 - 2c + (M-1) divide it.
OUT = "research/results/bmd-20261009-ad/tie-taylor-cofactor.txt";
default(parisizemax, 4 * 10^9);
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
{
  foreach([3, 4, 5], M, my(R = M * (M - 1) / 2, z = [2, 5, 11]);
    my(Y = concat(['c, 1], vector(M - 2, i, 'e * z[i])), P = matrix(R, R), r = 0);
    for (i = 1, M, for (j = i + 1, M, r++; my(h = H(Y[i], Y[j], R - 1)); for (k = 1, R, P[r, k] = h[k])));
    my(T = matdet(P), V = prod(i = 1, M, prod(j = i + 1, M, Y[i] - Y[j]))^(M - 2));
    my(Q = T / V, F = subst(Q, 'e, 0));
    my(m = 'c^0 * ((M - 1) * 'c^2 - 2 * 'c + (M - 1)));
    write(OUT, "M=", M, ": F(c,1,0..0) = ", factor(F));
    write(OUT, "  divisible by the Hankel modulus polynomial ", m, ": ", if(type(F) == "t_POL", (F % m) == 0, 0)));
}
