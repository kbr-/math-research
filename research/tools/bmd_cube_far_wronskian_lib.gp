\\ Shared definitions of the far spaces F_k (copied unchanged from bmd_cube_far_wronskian.gp).
Rn(n) = n*(2*n-1);
funcs(e, l) = {
  my(L = List());
  for (j = 0, Rn(e) - 1, listput(L, [0, 0, x^j]));
  listput(L, [0, -3, 1]);
  for (j = 0, Rn(l) - 1, listput(L, [-(Rn(l) + 2), 0, x^j]));
  for (j = 0, 4*e - 1, listput(L, [0, -7/2, x^j]));
  for (j = 0, 4*l - 1, listput(L, [1/2 - 4*l, -5/2, x^j]));
  for (j = 0, 4*e*l - 1, listput(L, [-7/2 + 4*e - 4*e*l, 0, x^j]));
  Vec(L);
}
