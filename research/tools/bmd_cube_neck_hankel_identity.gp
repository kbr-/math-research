\\ The cancellation at level 6 of the neck window (e,l,w,c) = (1,2,2,4) (cycle bmd-20260930-zzz): the Psi values of
\\ bmd_cube_neck_psi_pattern.gp take two values psi_a, psi_b with psi_b/psi_a = -1, so the level sum is psi_a times
\\   h12 h45 + h14 h34 + h23 h25 + h34 h23 - (h13 h35 + h24^2),   h_ij = t_i t_(j+1) - t_j t_(i+1).
\\ Check that this vanishes identically in symbolic t, i.e. is a relation among 2x2 minors of the 2 x infinity Hankel
\\ matrix; and whether the plain Pluecker relation of a generic 2 x 5 matrix (rows (t_q), (u_q)) also kills it.
{
  my(t = vector(8, i, eval(Str("t", i))), u = vector(8, i, eval(Str("u", i))));
  my(h(i, j) = t[i] * t[j + 1] - t[j] * t[i + 1]);
  my(g(i, j) = t[i] * u[j] - t[j] * u[i]);  \\ generic 2 x n minors, columns (t_q, u_q)
  my(F = h(1,2)*h(4,5) + h(1,4)*h(3,4) + h(2,3)*h(2,5) + h(3,4)*h(2,3) - (h(1,3)*h(3,5) + h(2,4)^2));
  my(Fg = g(1,2)*g(4,5) + g(1,4)*g(3,4) + g(2,3)*g(2,5) + g(3,4)*g(2,3) - (g(1,3)*g(3,5) + g(2,4)^2));
  print("Hankel minors: level-6 combination = ", F);
  print("generic 2 x n minors: same combination vanishes: ", Fg == 0, " (1 = yes, 0 = no)");
}
