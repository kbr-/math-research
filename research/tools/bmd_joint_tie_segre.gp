\\ Contact at a joint two-set tie (cycle bmd-20261009-bw, 9 October 2026).
\\ Statement tested (prop:cube-joint-tie-slack-zero): at a joint tie with C-block support {S, S'} (one swap) and cross
\\ support {Lam1, Lam2} (adjacent windows, union of 2M+1 columns, cross spread 2M), the limit space L0 = E + Q + U has a
\\ section of order R+1 only if its Plucker coordinates on J0 = T0, J1 = {0..R-2, R}, J2 = {0..R-3, R-1, R} vanish
\\ (the converse uses the proposition: orders lie in 0..R+1). By lem:cube-leading-wronskian-sum (a) each is a bilinear form
\\ sum_(X, Lam) pi_X gamma_Lam det D_(Y, J), Y = X u {-3} u (-3/2 + Lam) in block order, D_(e, j) = binom(e, j). Contact is
\\ possible for some leading data iff the 3 x 4 coefficient matrix has a kernel vector of rank one (k11 k22 = k12 k21) with
\\ all entries nonzero. Joint ties above the cone tie at the Gegenbauer zero -1 (m = 2, M = 4, R = 15), from
\\ joint-tie-cross-leaders.txt: (w_x, w_e) = (1, 1) and (1, 5).
OUT = "research/results/bmd-20261009-bw/joint-tie-segre.txt";
bin(e, j) = { my(r = 1); for (i = 0, j - 1, r *= (e - i)); r / j!; }
Dm(Y, J) = matdet(matrix(#Y, #J, a, b, bin(Y[a], J[b])));
{
  my(R = 15, S = [0, 1, 2, 3, 4, 5], Sp = [0, 1, 2, 3, 4, 6]);
  my(J0 = [0 .. 14], J1 = concat([0 .. 13], [15]), J2 = concat([0 .. 12], [14, 15]));
  my(ties = [[[1, 1], [-3 .. 4], [-2 .. 5]], [[1, 5], [-2 .. 5], [-1 .. 6]]]);
  foreach(ties, T, my([rate, L1, L2] = T, Xs = [S, Sp], Ls = [L1, L2], M = matrix(3, 4));
    for (a = 1, 2, for (c = 1, 2, my(Y = concat(concat(Xs[a], [-3]), apply(t -> -3/2 + t, Ls[c])));
      for (r = 1, 3, M[r, 2 * (a - 1) + c] = Dm(Y, [J0, J1, J2][r]))));
    my(K = matker(M));
    write(OUT, "joint tie at (w_x, w_e) = ", rate, ", cross leaders ", L1, ", ", L2, ": rank of the 3 x 4 form matrix ", matrank(M), ", kernel dimension ", #K);
    if (#K == 1, my(k = K[, 1], rk1 = (k[1] * k[4] == k[2] * k[3]), allnz = (k[1] * k[2] * k[3] * k[4] != 0));
      write(OUT, "   kernel vector (pi gamma, pi gamma', pi' gamma, pi' gamma') proportional to ", k~, "; rank one: ", rk1, ", all entries nonzero: ", allnz,
            "; contact possible for some leading data: ", rk1 && allnz)));
}
