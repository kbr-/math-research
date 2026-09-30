\\ Are the quadratic relations among the 2x2 minors h_ij = t_i t_(j+1) - t_j t_(i+1) (1 <= i < j <= n) of a 2 x n
\\ Hankel matrix spanned by two Pluecker systems? (cycle bmd-20261001-b)
\\   (P1) the Pluecker relations of the h_ij themselves: h_ij h_kl - h_ik h_jl + h_il h_jk = 0, i<j<k<l <= n;
\\   (P2) the Pluecker relations of k_ij = t_i t_(j+2) - t_j t_(i+2) = h_(i,j+1) + h_(i+1,j), i<j <= n-1 (minors of the
\\        2 x (n-1) matrix with rows (t_q), (t_(q+2))), rewritten as quadratic forms in the h (with h_ii = 0).
\\ For n = 5..9: dim span(P1 + P2) against the dimension of all relations (C(n,4) + C(n-1,4) observed), exactly over Q
\\ as vectors in the basis of products h_ab h_cd; and whether the level-6 relation of the (1,2,2,4) neck window lies in it.
default(parisizemax, 4000000000);
{
  for (n = 5, 9,
    my(S = List()); forsubset([n, 2], v, listput(S, Vec(v))); S = Vec(S);
    my(idx = Map()); for (i = 1, #S, mapput(idx, S[i], i));
    my(np = #S * (#S + 1) / 2, pid(a, b) = my(x = min(a, b), y = max(a, b)); (y - 1) * y / 2 + x);
    \\ h as a sparse vector over pairs: hv(i,j) returns [index, sign] or 0
    my(hv(i, j) = if (i == j, 0, if (i < j, [mapget(idx, [i, j]), 1], [mapget(idx, [j, i]), -1])));
    my(addprod(v, A, B, c) = foreach (A, a, foreach (B, b, v[pid(a[1], b[1])] += c * a[2] * b[2])); v);
    my(lin(i, j) = my(r = List(), x = hv(i, j)); if (x != 0, listput(r, x)); Vec(r));   \\ h_ij as list of [index, coeff]
    my(klin(i, j) = my(r = List(), x = hv(i, j + 1), y = hv(i + 1, j)); if (x != 0, listput(r, x)); if (y != 0, listput(r, y)); Vec(r));
    my(rows = List());
    forsubset([n, 4], q, my(i = q[1], j = q[2], k = q[3], l = q[4], v = vectorv(np));
      v = addprod(v, lin(i, j), lin(k, l), 1); v = addprod(v, lin(i, k), lin(j, l), -1); v = addprod(v, lin(i, l), lin(j, k), 1);
      listput(rows, v));
    my(r1 = matrank(Mat(Vec(rows))));
    forsubset([n - 1, 4], q, my(i = q[1], j = q[2], k = q[3], l = q[4], v = vectorv(np));
      v = addprod(v, klin(i, j), klin(k, l), 1); v = addprod(v, klin(i, k), klin(j, l), -1); v = addprod(v, klin(i, l), klin(j, k), 1);
      listput(rows, v));
    my(Mr = Mat(Vec(rows)), r12 = matrank(Mr));
    my(msg = "");
    if (n == 5,
      \\ the level-6 relation of the (1,2,2,4) window: h12 h45 + h14 h34 + h23 h25 + h23 h34 - h13 h35 - h24^2
      my(F = vectorv(np));
      F = addprod(F, lin(1,2), lin(4,5), 1); F = addprod(F, lin(1,4), lin(3,4), 1); F = addprod(F, lin(2,3), lin(2,5), 1);
      F = addprod(F, lin(2,3), lin(3,4), 1); F = addprod(F, lin(1,3), lin(3,5), -1); F = addprod(F, lin(2,4), lin(2,4), -1);
      msg = Str("; level-6 neck relation in span(P1+P2): ", matrank(matconcat([Mr, F])) == r12));
    print("n = ", n, ": rank P1 ", r1, " (C(n,4) = ", binomial(n, 4), "), rank P1+P2 ", r12, " (C(n,4)+C(n-1,4) = ", binomial(n, 4) + binomial(n - 1, 4), ")", msg));
}
